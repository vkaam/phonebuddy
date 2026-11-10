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
        })
        self.assertNotIn('do-not-log', serialized)
        self.assertNotIn('ContainerAppConsoleLogs', serialized)
        self.assertNotIn('+1-555-0100', serialized)

    def test_workspace_query_timeout_is_redacted_and_fails_closed(self):
        def timed_out_runner(*args, **kwargs):
            raise subprocess.TimeoutExpired(['az', 'monitor'], timeout=60)

        report = query_workspace_telemetry(
            'workspace-id', 'app-name', 'release-1', timed_out_runner)
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['reasons'], ['dependency_outage'])
        self.assertEqual(report['diagnostic'], {
            'operation': 'log_analytics_query', 'category': 'timeout',
            'exit_code': None,
        })
        self.assertNotIn('secret token', json.dumps(report))

    def test_workspace_query_escapes_filter_values(self):
        captured = {}

        def runner(command, **kwargs):
            captured['query'] = command[command.index('--analytics-query') + 1]
            return self.runner_for(100, 0)(command, **kwargs)

        query_workspace_telemetry('workspace-id', "app'name", "release'1", runner)
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
