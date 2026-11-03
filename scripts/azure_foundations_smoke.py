#!/usr/bin/env python3
"""Run synthetic, nonproduction data-plane checks against a deployed foundation."""
import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


def az_json(*args):
    result = subprocess.run(['az', *args, '--only-show-errors', '-o', 'json'],
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def token(resource):
    return subprocess.run(
        ['az', 'account', 'get-access-token', '--resource', resource,
         '--query', 'accessToken', '-o', 'tsv', '--only-show-errors'],
        text=True, capture_output=True, check=True,
    ).stdout.strip()


def request(url, method='GET', headers=None, body=None, expected=range(200, 300)):
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status, response_headers, content = response.status, response.headers, response.read()
    except urllib.error.HTTPError as exc:
        status, response_headers, content = exc.code, exc.headers, exc.read()
    if status not in expected:
        raise RuntimeError(f'{method} {urllib.parse.urlsplit(url).path} returned HTTP {status}')
    return status, response_headers, content


def resources(resource_group):
    items = az_json('resource', 'list', '--resource-group', resource_group)
    by_type = {}
    for item in items:
        by_type.setdefault(item.get('type', '').lower(), []).append(item)
    def one(resource_type):
        matches = by_type.get(resource_type.lower(), [])
        if len(matches) != 1:
            raise RuntimeError(f'Expected exactly one deployed {resource_type}')
        return matches[0]
    return one


def check_blob(one, run_id):
    storage = one('Microsoft.Storage/storageAccounts')
    account = storage['name']
    blob_name = f'foundation-smoke/{run_id}.txt'
    url = f'https://{account}.blob.core.windows.net/calls/{blob_name}'
    headers = {
        'Authorization': f"Bearer {token('https://storage.azure.com/')}",
        'x-ms-version': '2023-11-03', 'x-ms-blob-type': 'BlockBlob',
        'Content-Type': 'text/plain',
    }
    request(url, 'PUT', headers, b'Phonebuddy synthetic foundation smoke data')
    request(url, 'GET', expected=(401, 403, 404))
    request(url, 'DELETE', headers)


def service_bus(one, run_id):
    namespace = one('Microsoft.ServiceBus/namespaces')['name']
    base = f'https://{namespace}.servicebus.windows.net/foundation-smoke'
    audience = 'https://servicebus.azure.net/'
    bearer = {'Authorization': f'Bearer {token(audience)}',
              'Content-Type': 'application/atom+xml;type=entry;charset=utf-8'}
    message_id = f'phonebuddy-{run_id}'
    send_headers = dict(bearer)
    send_headers['BrokerProperties'] = json.dumps({'MessageId': message_id})
    request(f'{base}/messages', 'POST', send_headers,
            b'Phonebuddy synthetic dead-letter probe')
    request(f'{base}/messages', 'POST', {'Content-Type': 'text/plain'},
            b'unauthorized synthetic probe', expected=(401, 403))

    # Abandon each peek-locked delivery. The queue's maxDeliveryCount moves it to DLQ.
    for _ in range(5):
        status, headers, _ = request(f'{base}/messages/head?timeout=10', 'POST', bearer,
                                     expected=(200, 201, 204, 404))
        location = headers.get('Location')
        if status == 404 or not location:
            break
        locked_url = urllib.parse.urljoin(base + '/', location)
        parsed = urllib.parse.urlsplit(locked_url)
        if parsed.hostname != f'{namespace}.servicebus.windows.net':
            raise RuntimeError('Service Bus lock URL escaped the expected namespace')
        request(locked_url, 'DELETE', bearer, expected=(200, 202, 204))
        time.sleep(1)

    dlq = f'{base}/$deadletterqueue/messages/head?timeout=10'
    status, headers, _ = request(dlq, 'POST', bearer, expected=(200, 201, 204, 404))
    if status == 404 or not headers.get('Location'):
        raise RuntimeError('Synthetic queue message did not reach the dead-letter queue')
    locked_url = urllib.parse.urljoin(base + '/', headers['Location'])
    if urllib.parse.urlsplit(locked_url).hostname != f'{namespace}.servicebus.windows.net':
        raise RuntimeError('Dead-letter lock URL escaped the expected namespace')
    request(locked_url, 'DELETE', bearer, expected=(200, 202, 204))


def speech(one):
    items = az_json('resource', 'list', '--resource-group',
                    one('Microsoft.Sql/servers')['resourceGroup'])
    speech_account = next((item for item in items
                           if item.get('kind') == 'SpeechServices'), None)
    if not speech_account:
        raise RuntimeError('Speech account was not found')
    endpoint = speech_account.get('properties', {}).get('endpoint')
    if not endpoint:
        endpoint = f"https://{speech_account['name']}.cognitiveservices.azure.com/"
    url = urllib.parse.urljoin(endpoint.rstrip('/') + '/', 'cognitiveservices/v1')
    body = (b'<speak version="1.0" xml:lang="en-US"><voice name="en-US-JennyNeural">'
            b'Phonebuddy synthetic infrastructure smoke test.</voice></speak>')
    headers = {'Authorization': f"Bearer {token('https://cognitiveservices.azure.com')}",
               'Content-Type': 'application/ssml+xml',
               'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm'}
    request(url, 'POST', headers, body)
    request(url, 'POST', {'Content-Type': 'application/ssml+xml'}, body,
            expected=(401, 403))


def foundry(one):
    items = az_json('resource', 'list', '--resource-group', one('Microsoft.Sql/servers')['resourceGroup'])
    account = next((item for item in items
                    if item.get('type', '').lower() == 'microsoft.cognitiveservices/accounts'
                    and item.get('kind') == 'AIServices'), None)
    if not account:
        raise RuntimeError('Foundry account was not found')
    endpoint = account.get('properties', {}).get('endpoint')
    if not endpoint:
        raise RuntimeError('Foundry account endpoint is missing')
    deployment = az_json('resource', 'list', '--resource-group', account['resourceGroup'])
    deployment = next((item for item in deployment
                       if item.get('type', '').lower() ==
                       'microsoft.cognitiveservices/accounts/deployments'), None)
    if not deployment:
        raise RuntimeError('Foundry model deployment was not found')
    name = deployment['name'].split('/')[-1]
    url = urllib.parse.urljoin(endpoint.rstrip('/') + '/', 'openai/v1/chat/completions')
    body = json.dumps({'model': name, 'messages': [{'role': 'user', 'content': 'Reply OK'}],
                       'max_completion_tokens': 2}).encode()
    headers = {'Authorization': f"Bearer {token('https://cognitiveservices.azure.com')}",
               'Content-Type': 'application/json'}
    request(url, 'POST', headers, body)
    request(url, 'POST', {'Content-Type': 'application/json'}, body,
            expected=(401, 403))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', required=True, choices=('dev', 'test'),
                        help='production is intentionally not supported')
    parser.add_argument('--subscription-id', required=True,
                        help='subscription containing the deployed foundation')
    options = parser.parse_args()
    current = az_json('account', 'show')
    if current.get('id', '').lower() != options.subscription_id.lower():
        raise RuntimeError('Active Azure CLI subscription does not match --subscription-id')
    location = 'westeurope'
    group = f'rg-pb-{options.environment}-{location}-foundation'
    one = resources(group)
    run_id = str(uuid.uuid4())
    checks = [('blob authorized/denied', lambda: check_blob(one, run_id)),
              ('Service Bus authorized/denied/dead-letter', lambda: service_bus(one, run_id)),
              ('Speech authorized/denied', lambda: speech(one)),
              ('Foundry authorized/denied inference', lambda: foundry(one))]
    passed = []
    for name, check in checks:
        check()
        passed.append(name)
        print(f'PASS {name}')
    print(f'Completed {len(passed)} synthetic checks in {options.environment}; no production data used')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as exc:
        detail = getattr(exc, 'stderr', None)
        print(f'Foundation smoke failed: {exc}', file=sys.stderr)
        if detail:
            print(detail.strip(), file=sys.stderr)
        sys.exit(1)
