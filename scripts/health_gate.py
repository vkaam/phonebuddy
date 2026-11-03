#!/usr/bin/env python3
"""Run a fail-closed versioned HTTP readiness and observation gate."""
import argparse
from datetime import datetime, timezone
import json
import math
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import urlopen


def safe_base_url(value):
    """Require a plain HTTPS origin/path and discard query or user info."""
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Target must be an HTTPS URL without user information')
    if parsed.query or parsed.fragment:
        raise ValueError('Target URL must not include a query string or fragment')
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip('/'), '', ''))


def percentile95(values):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def check_response(base_url, route, expected_version, timeout):
    started = time.monotonic()
    result = {'status': None, 'duration_ms': None, 'failure': None}
    try:
        with urlopen(base_url + route, timeout=timeout) as response:
            result['status'] = response.status
            payload = json.load(response)
        if not isinstance(payload, dict) or payload.get('ready') is not True:
            result['failure'] = 'unhealthy_response'
        elif payload.get('version') != expected_version:
            result['failure'] = 'version_mismatch'
        elif result['status'] < 200 or result['status'] >= 300:
            result['failure'] = 'unhealthy_response'
    except HTTPError as error:
        result['status'] = error.code
        result['failure'] = 'unhealthy_response'
    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        result['failure'] = 'dependency_outage'
    result['duration_ms'] = round((time.monotonic() - started) * 1000, 3)
    return result


def evaluate_samples(samples, minimum_requests=100, error_limit=0.01, latency_limit_ms=2000):
    """Return a compact evidence report, failing closed on missing samples."""
    responses = [response for sample in samples for response in sample]
    failures = [response for response in responses if response['failure']]
    durations = [response['duration_ms'] for response in responses
                 if response['duration_ms'] is not None]
    errors = [response for response in responses
              if response['status'] is None or response['status'] >= 500]
    reasons = []
    if len(responses) < minimum_requests:
        reasons.append('insufficient_samples')
    if not responses or len(durations) != len(responses):
        reasons.append('missing_telemetry')
    if any(response['failure'] == 'dependency_outage' for response in failures):
        reasons.append('dependency_outage')
    if any(response['failure'] in ('unhealthy_response', 'version_mismatch')
           for response in failures):
        reasons.append('unhealthy_response')
    for index in range(0, len(samples), 5):
        window = [response for sample in samples[index:index + 5] for response in sample]
        window_number = index // 5 + 1
        if len(samples[index:index + 5]) < 5 or not window:
            reasons.append(f'missing_sample_window_{window_number}')
        window_errors = sum(response['status'] is None or response['status'] >= 500
                            for response in window)
        if window and window_errors / len(window) >= error_limit:
            reasons.append(f'error_rate_window_{window_number}')
        window_latencies = [response['duration_ms'] for response in window
                            if response['duration_ms'] is not None]
        if window_latencies and percentile95(window_latencies) >= latency_limit_ms:
            reasons.append(f'latency_window_{window_number}')
    total_error_rate = len(errors) / len(responses) if responses else 1.0
    p95 = percentile95(durations)
    if total_error_rate >= error_limit:
        reasons.append('error_rate')
    if p95 is None:
        reasons.append('missing_telemetry')
    elif p95 >= latency_limit_ms:
        reasons.append('latency')
    return {
        'status': 'pass' if not reasons else 'fail',
        'request_count': len(responses),
        'error_rate': round(total_error_rate, 4),
        'p95_latency_ms': p95,
        'failure_counts': {
            reason: sum(response['failure'] == reason for response in failures)
            for reason in ('unhealthy_response', 'version_mismatch', 'dependency_outage')
        },
        'reasons': sorted(set(reasons)),
    }


def run_gate(url, expected_version, warmup_seconds=60, observation_seconds=600,
             sample_interval_seconds=60, requests_per_sample=10, timeout_seconds=5,
             sleeper=time.sleep, clock=time.monotonic):
    if warmup_seconds < 0 or observation_seconds < 300 or sample_interval_seconds <= 0:
        raise ValueError('Warm-up must be nonnegative and observation at least five minutes')
    if requests_per_sample < 1 or timeout_seconds <= 0 or not expected_version:
        raise ValueError('Expected version, requests per sample, and timeout are required')
    base = safe_base_url(url)
    sleeper(warmup_seconds)
    samples = []
    deadline = clock() + observation_seconds
    while clock() < deadline:
        sample = []
        for request_index in range(requests_per_sample):
            route = '/ready' if request_index % 2 == 0 else '/'
            sample.append(check_response(base, route, expected_version, timeout_seconds))
        samples.append(sample)
        remaining = deadline - clock()
        if remaining <= 0:
            break
        sleeper(min(sample_interval_seconds, remaining))
    report = evaluate_samples(samples)
    report['observed_at'] = datetime.now(timezone.utc).isoformat()
    report['observation_window_seconds'] = observation_seconds
    report['sample_window_count'] = len(samples)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True, help='HTTPS service base URL; no query or fragment')
    parser.add_argument('--expected-version', required=True)
    parser.add_argument('--warmup-seconds', type=int, default=60)
    parser.add_argument('--observation-seconds', type=int, default=600)
    parser.add_argument('--sample-interval-seconds', type=int, default=60)
    parser.add_argument('--requests-per-sample', type=int, default=10)
    parser.add_argument('--timeout-seconds', type=float, default=5)
    args = parser.parse_args(argv)
    try:
        report = run_gate(args.url, args.expected_version, args.warmup_seconds,
                          args.observation_seconds, args.sample_interval_seconds,
                          args.requests_per_sample, args.timeout_seconds)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(report, sort_keys=True))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
