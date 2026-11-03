"""Test the release health gate's fail-closed evidence rules."""
import unittest

from scripts.health_gate import evaluate_samples, safe_base_url


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


if __name__ == '__main__':
    unittest.main()
