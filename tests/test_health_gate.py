"""Test the release health gate's fail-closed evidence rules."""
import unittest

import json
import subprocess

from scripts.health_gate import (
    evaluate_samples, query_workspace_telemetry, safe_base_url, wait_for_workspace_telemetry,
)


def response(status=200, duration=25, failure=None):
    return {'status': status, 'duration_ms': duration, 'failure': failure}


class HealthGateEvaluationTests(unittest.TestCase):
    def test_healthy_observation_passes_with_required_samples(self):
        report = evaluate_samples([[response() for _ in range(10)] for _ in range(10)])
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['request_count'], 100)

    def test_missing_telemetry_and_insufficient_samples_fail_closed(self):
        report = evaluate_samples([])
        self.assertEqual(report['status'], 'fail')
        self.assertIn('missing_telemetry', report['reasons'])
        self.assertIn('insufficient_samples', report['reasons'])

    def test_unhealthy_statuses_and_wrong_versions_fail(self):
        samples = [[response() for _ in range(9)] + [response(500, failure='unhealthy_response')]
                   for _ in range(10)]
        report = evaluate_samples(samples)
        self.assertIn('error_rate', report['reasons'])
        samples[0][0] = response(failure='version_mismatch')
        report = evaluate_samples(samples)
        self.assertIn('unhealthy_response', report['reasons'])

    def test_latency_and_dependency_outage_are_distinguished(self):
        slow = [[response(duration=2100) for _ in range(10)] for _ in range(10)]
        self.assertIn('latency', evaluate_samples(slow)['reasons'])
        outage = [[response(status=None, duration=None, failure='dependency_outage')
                   for _ in range(10)] for _ in range(10)]
        report = evaluate_samples(outage)
        self.assertIn('dependency_outage', report['reasons'])
        self.assertIn('missing_telemetry', report['reasons'])

    def test_target_query_and_user_info_are_rejected(self):
        with self.assertRaises(ValueError):
            safe_base_url('https://example.test/path?token=secret')
        with self.assertRaises(ValueError):
            safe_base_url('https://user:secret@example.test/path')


class WorkspaceTelemetryTests(unittest.TestCase):
    def runner_for(self, event_count, unhealthy_count):
        payload = [{'telemetry_event_count': str(event_count),
                    'unhealthy_event_count': str(unhealthy_count)}]
        return lambda *args, **kwargs: type('Result', (), {
            'returncode': 0, 'stdout': json.dumps(payload), 'stderr': ''})()

    def test_workspace_telemetry_requires_one_hundred_matching_events(self):
        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', self.runner_for(100, 0))
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(report['telemetry_event_count'], 100)

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', self.runner_for(99, 0))
        self.assertEqual(report['reasons'], ['missing_telemetry'])

    def test_throttled_query_retries_with_bounded_backoff_then_recovers(self):
        throttled = type('Result', (), {
            'returncode': 1, 'stdout': '', 'stderr': 'HTTP 429 throttled; query=secret',
        })()
        succeeded = type('Result', (), {
            'returncode': 0,
            'stdout': json.dumps([{'telemetry_event_count': '100', 'unhealthy_event_count': '0'}]),
            'stderr': '',
        })()
        results = iter([throttled, throttled, succeeded])
        calls, sleeps = [], []

        def runner(*args, **kwargs):
            calls.append(args[0])
            return next(results)

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', runner, sleeper=sleeps.append)
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [10, 20])

    def test_exhausted_throttle_retries_remain_redacted_dependency_outage(self):
        calls, sleeps = [], []

        def runner(*args, **kwargs):
            calls.append(args[0])
            return type('Result', (), {
                'returncode': 1, 'stdout': '',
                'stderr': 'HTTP 429 throttled; query=secret; caller=private',
            })()

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', runner, sleeper=sleeps.append)
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['reasons'], ['dependency_outage'])
        self.assertEqual(report['diagnostic'], {
            'operation': 'log_analytics_query', 'category': 'throttled', 'exit_code': 1,
            'error_code': None, 'error_source': 'stderr', 'http_status': 429,
        })
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [10, 20, 30])
        self.assertNotIn('secret', json.dumps(report))
        self.assertNotIn('private', json.dumps(report))

    def test_non_throttle_query_errors_are_not_retried(self):
        for stderr, category in [('AuthorizationFailed: forbidden', 'authorization_denied'),
                                 ('Semantic error in query', 'query_rejected')]:
            with self.subTest(category=category):
                calls, sleeps = [], []

                def runner(*args, **kwargs):
                    calls.append(args[0])
                    return type('Result', (), {
                        'returncode': 1, 'stdout': '', 'stderr': stderr,
                    })()

                report = query_workspace_telemetry(
                    'workspace-id', 'app-name', 'release-1', runner,
                    sleeper=sleeps.append)
                self.assertEqual(report['status'], 'fail')
                self.assertEqual(report['diagnostic']['category'], category)
                self.assertEqual(len(calls), 1)
                self.assertEqual(sleeps, [])

    def test_workspace_unhealthy_events_and_query_failures_block(self):
        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', self.runner_for(100, 1))
        self.assertEqual(report['reasons'], ['unhealthy_response'])

        def failed_runner(*args, **kwargs):
            return type('Result', (), {'returncode': 1, 'stdout': '', 'stderr': 'denied'})()

        report = query_workspace_telemetry('workspace-id', 'app-name', 'release-1', failed_runner)
        self.assertEqual(report['reasons'], ['dependency_outage'])
        self.assertEqual(report['diagnostic'], {
            'operation': 'log_analytics_query', 'category': 'cli_error', 'exit_code': 1,
            'error_code': None, 'error_source': 'stderr', 'http_status': None,
        })

    def test_workspace_query_diagnostic_classifies_auth_errors_without_echoing_cli_output(self):
        sensitive_stderr = (
            'AuthorizationFailed: Bearer token=do-not-log; '
            'query=ContainerAppConsoleLogs; caller=+1-555-0100'
        )

        def failed_runner(*args, **kwargs):
            return type('Result', (), {
                'returncode': 1, 'stdout': '', 'stderr': sensitive_stderr,
            })()

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', failed_runner)
        serialized = json.dumps(report)
        self.assertEqual(report['diagnostic'], {
            'operation': 'log_analytics_query',
            'category': 'authorization_denied',
            'exit_code': 1,
            'error_code': 'AuthorizationFailed',
            'error_source': 'stderr',
            'http_status': None,
        })
        self.assertNotIn('do-not-log', serialized)
        self.assertNotIn('ContainerAppConsoleLogs', serialized)
        self.assertNotIn('+1-555-0100', serialized)

    def test_workspace_query_reports_sanitized_provider_error_code(self):
        sensitive_stderr = (
            'ERROR: (BadRequest) workspace=123e4567-e89b-12d3-a456-426614174000 '
            'query=ContainerAppConsoleLogs; Bearer token=do-not-log'
        )

        def failed_runner(*args, **kwargs):
            return type('Result', (), {
                'returncode': 1, 'stdout': '', 'stderr': sensitive_stderr,
            })()

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', failed_runner)
        serialized = json.dumps(report)
        self.assertEqual(report['diagnostic'], {
            'operation': 'log_analytics_query', 'category': 'query_rejected',
            'exit_code': 1, 'error_code': 'BadRequest', 'error_source': 'stderr',
            'http_status': None,
        })
        self.assertNotIn('123e4567-e89b-12d3-a456-426614174000', serialized)
        self.assertNotIn('ContainerAppConsoleLogs', serialized)
        self.assertNotIn('do-not-log', serialized)

    def test_workspace_query_timeout_is_redacted_and_fails_closed(self):
        def timed_out_runner(*args, **kwargs):
            raise subprocess.TimeoutExpired(['az', 'monitor'], timeout=60)

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', timed_out_runner)
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['reasons'], ['dependency_outage'])
        self.assertEqual(report['diagnostic'], {
            'operation': 'log_analytics_query', 'category': 'timeout',
            'exit_code': None, 'error_code': None, 'error_source': 'none',
            'http_status': None,
        })
        self.assertNotIn('secret token', json.dumps(report))

    def test_workspace_query_extracts_safe_error_code_from_stdout(self):
        sensitive_stdout = json.dumps({
            'error': {
                'code': 'TooManyRequests',
                'message': 'query=private; Bearer token=do-not-log',
            },
        })

        def failed_runner(*args, **kwargs):
            return type('Result', (), {
                'returncode': 1, 'stdout': sensitive_stdout, 'stderr': '',
            })()

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', failed_runner)
        serialized = json.dumps(report)
        self.assertEqual(report['diagnostic'], {
            'operation': 'log_analytics_query', 'category': 'throttled',
            'exit_code': 1, 'error_code': 'TooManyRequests', 'error_source': 'stdout',
            'http_status': None,
        })
        self.assertNotIn('private', serialized)
        self.assertNotIn('do-not-log', serialized)

    def test_workspace_query_classifies_safe_http_status_without_echoing_output(self):
        examples = [
            ('ERROR: request failed with status code: 403; resource=private',
             'authorization_denied', 403),
            ('HTTP/1.1 404 Not Found; workspace=private',
             'workspace_not_found', 404),
            ('{"status":400,"message":"query=private"}',
             'query_rejected', 400),
            ('HTTP 503; token=do-not-log', 'provider_error', 503),
        ]
        for stderr, category, status in examples:
            with self.subTest(status=status):
                def failed_runner(*args, **kwargs):
                    return type('Result', (), {
                        'returncode': 1, 'stdout': '', 'stderr': stderr,
                    })()

                report = query_workspace_telemetry(
                    'workspace-id', 'app-name', 'release-1', failed_runner)
                serialized = json.dumps(report)
                self.assertEqual(report['diagnostic']['category'], category)
                self.assertEqual(report['diagnostic']['http_status'], status)
                self.assertEqual(report['diagnostic']['error_source'], 'stderr')
                self.assertNotIn('private', serialized)
                self.assertNotIn('do-not-log', serialized)

    def test_workspace_query_escapes_filter_values(self):
        captured = {}

        def runner(command, **kwargs):
            captured['query'] = command[command.index('--analytics-query') + 1]
            return self.runner_for(100, 0)(command, **kwargs)

        query_workspace_telemetry('workspace-id', "app'name", "release'1", runner)
        self.assertIn("""Log contains '"event":"health_request"'""", captured['query'])
        self.assertLess(captured['query'].index('Log contains'),
                        captured['query'].index('| extend health='))
        self.assertIn("ContainerAppName == 'app''name'", captured['query'])
        self.assertIn("health.version) == 'release''1'", captured['query'])

    def test_missing_events_are_polled_for_bounded_ingestion_delay(self):
        reports = iter([
            {'status': 'fail', 'reasons': ['missing_telemetry'], 'telemetry_event_count': 0},
            {'status': 'pass', 'reasons': [], 'telemetry_event_count': 100},
        ])
        sleeps = []
        report = wait_for_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', max_wait_seconds=60,
            poll_interval_seconds=30, query=lambda *_args: next(reports),
            sleeper=sleeps.append, clock=lambda: 0 if not sleeps else 30,
        )
        self.assertEqual(report['status'], 'pass')
        self.assertEqual(sleeps, [30])

    def test_unhealthy_or_unavailable_workspace_does_not_wait(self):
        sleeps = []
        for reason in ('unhealthy_response', 'dependency_outage'):
            report = {'status': 'fail', 'reasons': [reason]}
            actual = wait_for_workspace_telemetry(
                'workspace-id', 'app-name', 'release-1',
                query=lambda *_args, value=report: value, sleeper=sleeps.append,
            )
            self.assertEqual(actual, report)
        self.assertEqual(sleeps, [])


if __name__ == '__main__':
    unittest.main()
