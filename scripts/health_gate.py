#!/usr/bin/env python3
"""Run a fail-closed versioned HTTP readiness and observation gate."""
import argparse
from datetime import datetime, timezone
import json
import math
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import urlopen

MAX_QUERY_THROTTLE_RETRIES = 3
QUERY_THROTTLE_RETRY_BASE_SECONDS = 10
QUERY_THROTTLE_RETRY_MAX_SECONDS = 30


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


def workspace_query_failure_diagnostic(result):
    """Return bounded, redacted metadata for a failed Azure CLI query."""
    stderr = getattr(result, 'stderr', '')
    if not isinstance(stderr, str):
        stderr = ''
    # Inspect only a small prefix and map it to fixed labels. Never return CLI
    # output, query text, resource identifiers, or caller data.
    summary = stderr[:4096].casefold()
    if ('does not have authorization' in summary or 'authorizationfailed' in summary
            or 'forbidden' in summary):
        category = 'authorization_denied'
    elif ('unauthorized' in summary or 'authenticationfailed' in summary
          or 'expired token' in summary):
        category = 'authentication_failed'
    elif ('workspace not found' in summary or 'resourcenotfound' in summary):
        category = 'workspace_not_found'
    elif ('invalidquery' in summary or 'badargumenterror' in summary
          or 'semantic error' in summary):
        category = 'query_rejected'
    elif ('throttl' in summary or 'too many requests' in summary or '429' in summary):
        category = 'throttled'
    elif ('timed out' in summary or 'timeout' in summary):
        category = 'timeout'
    else:
        category = 'cli_error'
    exit_code = getattr(result, 'returncode', None)
    if not isinstance(exit_code, int) or isinstance(exit_code, bool) or not 0 <= exit_code <= 255:
        exit_code = None
    return {'operation': 'log_analytics_query', 'category': category,
            'exit_code': exit_code}


def query_workspace_telemetry(workspace_id, app_name, expected_version, runner=subprocess.run,
                              sleeper=time.sleep):
    """Require enough version-matched health events and no unhealthy responses."""
    if not workspace_id or not app_name or not expected_version:
        return {'status': 'fail', 'telemetry_event_count': 0,
                'unhealthy_event_count': 0, 'reasons': ['dependency_outage']}
    quote = lambda value: "'" + value.replace("'", "''") + "'"
    query = (
        'ContainerAppConsoleLogs '
        f'| where ContainerAppName == {quote(app_name)} '
        '| where TimeGenerated > ago(15m) '
        '| where Log contains \'"event":"health_request"\' '
        '| extend health=parse_json(substring(Log, indexof(Log, \'{\'))) '
        '| where tostring(health.event) == "health_request" '
        f'| where tostring(health.version) == {quote(expected_version)} '
        '| summarize telemetry_event_count=countif(todouble(health.duration_ms) >= 0), '
        'unhealthy_event_count=countif(toint(health.status) != 200)'
    )
    try:
        command = ['az', 'monitor', 'log-analytics', 'query', '--workspace', workspace_id,
                   '--analytics-query', query, '--output', 'json']
        for attempt in range(MAX_QUERY_THROTTLE_RETRIES + 1):
            result = runner(
                command, check=False, capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                break
            diagnostic = workspace_query_failure_diagnostic(result)
            if diagnostic['category'] != 'throttled' or attempt == MAX_QUERY_THROTTLE_RETRIES:
                return {'status': 'fail', 'telemetry_event_count': 0,
                        'unhealthy_event_count': 0, 'reasons': ['dependency_outage'],
                        'diagnostic': diagnostic}
            delay = min(QUERY_THROTTLE_RETRY_BASE_SECONDS * (2 ** attempt),
                        QUERY_THROTTLE_RETRY_MAX_SECONDS)
            sleeper(delay)
        payload = json.loads(result.stdout)
        if (not isinstance(payload, list) or len(payload) != 1
                or not isinstance(payload[0], dict)):
            raise ValueError('Log Analytics query returned an unexpected result')
        row = payload[0]
        telemetry_count = int(row['telemetry_event_count'])
        unhealthy_count = int(row['unhealthy_event_count'])
        if telemetry_count < 100:
            reasons = ['missing_telemetry']
        else:
            reasons = []
        if unhealthy_count:
            reasons.append('unhealthy_response')
        return {
            'status': 'pass' if not reasons else 'fail',
            'telemetry_event_count': telemetry_count,
            'unhealthy_event_count': unhealthy_count,
            'reasons': reasons,
        }
    except subprocess.TimeoutExpired:
        category = 'timeout'
    except FileNotFoundError:
        category = 'cli_unavailable'
    except (subprocess.SubprocessError, OSError):
        category = 'cli_execution_error'
    except (ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
        category = 'invalid_response'
    else:
        category = None
    if category:
        return {'status': 'fail', 'telemetry_event_count': 0,
                'unhealthy_event_count': 0, 'reasons': ['dependency_outage'],
                'diagnostic': {'operation': 'log_analytics_query', 'category': category,
                               'exit_code': None}}


def wait_for_workspace_telemetry(workspace_id, app_name, expected_version,
                                 max_wait_seconds=300, poll_interval_seconds=30,
                                 query=query_workspace_telemetry, sleeper=time.sleep,
                                 clock=time.monotonic):
    """Allow bounded ingestion lag before failing on missing workspace events."""
    if max_wait_seconds < 0 or poll_interval_seconds <= 0:
        raise ValueError('Telemetry wait must be nonnegative with a positive polling interval')
    deadline = clock() + max_wait_seconds
    while True:
        report = query(workspace_id, app_name, expected_version)
        if (report['status'] == 'pass' or 'unhealthy_response' in report['reasons']
                or 'dependency_outage' in report['reasons']):
            return report
        remaining = deadline - clock()
        if remaining <= 0:
            return report
        sleeper(min(poll_interval_seconds, remaining))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True, help='HTTPS service base URL; no query or fragment')
    parser.add_argument('--expected-version', required=True)
    parser.add_argument('--workspace-id', required=True, help='Log Analytics workspace customer ID')
    parser.add_argument('--app-name', required=True, help='Azure Container App name')
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
        telemetry = wait_for_workspace_telemetry(
            args.workspace_id, args.app_name, args.expected_version)
        report['workspace_telemetry'] = telemetry
        report['reasons'] = sorted(set(report['reasons'] + telemetry['reasons']))
        report['status'] = 'pass' if report['status'] == 'pass' and telemetry['status'] == 'pass' else 'fail'
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(report, sort_keys=True))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
