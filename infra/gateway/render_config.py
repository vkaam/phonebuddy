#!/usr/bin/env python3
"""Render gateway templates from server-side runtime values without logging secrets."""
import argparse
import ipaddress
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parent
REQUIRED = (
    'GATEWAY_PRIVATE_IP', 'GATEWAY_PUBLIC_IP', 'GATEWAY_FQDN',
    'WEBRTC_TEST_PASSWORD', 'TURN_SHARED_SECRET',
)
TEMPLATES = {
    ROOT / 'asterisk' / 'http.conf.template': 'http.conf',
    ROOT / 'asterisk' / 'pjsip.conf.template': 'pjsip.conf',
    ROOT / 'coturn' / 'turnserver.conf.template': 'turnserver.conf',
}
PLACEHOLDERS = {
    '__GATEWAY_PRIVATE_IP__': 'GATEWAY_PRIVATE_IP',
    '__GATEWAY_PUBLIC_IP__': 'GATEWAY_PUBLIC_IP',
    '__GATEWAY_FQDN__': 'GATEWAY_FQDN',
    '__WEBRTC_TEST_PASSWORD__': 'WEBRTC_TEST_PASSWORD',
    '__TURN_SHARED_SECRET__': 'TURN_SHARED_SECRET',
}


def runtime_values(environment):
    """Validate the complete, non-empty runtime configuration."""
    missing = [name for name in REQUIRED if not environment.get(name)]
    if missing:
        raise ValueError('Missing required gateway runtime values: ' + ', '.join(missing))
    values = {name: environment[name] for name in REQUIRED}
    private = ipaddress.ip_address(values['GATEWAY_PRIVATE_IP'])
    public = ipaddress.ip_address(values['GATEWAY_PUBLIC_IP'])
    if private.version != 4 or not private.is_private or private.is_loopback:
        raise ValueError('GATEWAY_PRIVATE_IP must be a private IPv4 address')
    if public.version != 4 or not public.is_global:
        raise ValueError('GATEWAY_PUBLIC_IP must be a public IPv4 address')
    if not re.fullmatch(r'(?=.{1,253}\Z)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}',
                        values['GATEWAY_FQDN']):
        raise ValueError('GATEWAY_FQDN must be a fully qualified DNS name')
    for name in ('WEBRTC_TEST_PASSWORD', 'TURN_SHARED_SECRET'):
        value = values[name]
        if len(value) < 32 or any(char in value for char in '\r\n\x00'):
            raise ValueError(f'{name} must be at least 32 characters without line breaks')
    return values


def render_text(template, values):
    rendered = template
    for placeholder, name in PLACEHOLDERS.items():
        rendered = rendered.replace(placeholder, values[name])
    remaining = re.findall(r'__[A-Z0-9_]+__', rendered)
    if remaining:
        raise ValueError('Gateway template contains unrecognized placeholders')
    return rendered


def write_private_file(path, content):
    """Atomically write one root-owned-by-caller config with owner-only access."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix='.gateway-', dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def render(output_dir, environment=None):
    values = runtime_values(os.environ if environment is None else environment)
    output_dir = Path(output_dir)
    if output_dir.is_symlink():
        raise ValueError('Output directory must not be a symbolic link')
    existed = output_dir.exists()
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    if existed and output_dir.stat().st_mode & 0o077:
        raise ValueError('Existing output directory must be private to its owner')
    rendered = {}
    for source, name in TEMPLATES.items():
        destination = output_dir / name
        if destination.is_symlink():
            raise ValueError(f'Refusing to replace symbolic link: {name}')
        rendered[name] = render_text(source.read_text(encoding='utf-8'), values)
        write_private_file(destination, rendered[name])
    return tuple(sorted(rendered))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='protected runtime directory for rendered configuration')
    args = parser.parse_args()
    names = render(args.output_dir)
    print('Rendered gateway configuration: ' + ', '.join(names))


if __name__ == '__main__':
    main()
