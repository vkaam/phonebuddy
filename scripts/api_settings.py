"""Validate public API runtime settings and write them as ARM deployment parameters.

The values are public identifiers, never secrets. A release must not deploy an
API that cannot validate tokens or reach its database, so placeholders and
missing values fail here, before any Azure preview or deployment.
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys

# environment variable -> (Bicep parameter, shape)
SETTINGS = {
    'ENTRA_TENANT_ID': ('entraTenantId', 'guid'),
    'ENTRA_API_CLIENT_ID': ('entraApiClientId', 'guid'),
    'SQL_SERVER': ('sqlServer', 'sql-server'),
    'SQL_DATABASE': ('sqlDatabase', 'name'),
    'SQL_MANAGED_IDENTITY_CLIENT_ID': ('sqlManagedIdentityClientId', 'guid'),
}
_GUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
_SQL_SERVER = re.compile(r'[a-z0-9][a-z0-9-]{0,62}\.database\.windows\.net')
_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}')
_PLACEHOLDERS = {
    'unresolved', 'placeholder', 'changeme', 'change-me', 'todo', 'tbd', 'example',
    'none', 'null', 'undefined', 'your-value-here', 'xxx',
}
_SHAPE_HINT = {
    'guid': 'a GUID with real digits',
    'sql-server': 'the full Azure SQL server hostname <name>.database.windows.net (a bare server name is not accepted)',
    'name': 'a database name',
}


def problems(values):
    """Return one clear message for each missing, placeholder or malformed setting."""
    found = []
    for name, (_, shape) in SETTINGS.items():
        value = (values.get(name) or '').strip()
        if not value:
            found.append(f'{name} is missing; set the matching dev Actions Variable.')
            continue
        lowered = value.lower()
        if (lowered in _PLACEHOLDERS or re.fullmatch(r'[<\[{].*[>\]}]', value)
                or 'placeholder' in lowered or 'unresolved' in lowered):
            found.append(f'{name} is a placeholder ({value!r}); supply the real public value.')
            continue
        pattern = {'guid': _GUID, 'sql-server': _SQL_SERVER, 'name': _NAME}[shape]
        if pattern.fullmatch(lowered if shape != 'name' else value) is None:
            found.append(f'{name} is malformed; expected {_SHAPE_HINT[shape]}.')
        elif shape == 'guid' and set(lowered) <= {'0', '-'}:
            found.append(f'{name} is the all-zero placeholder GUID; supply the real public value.')
    return found


def arm_parameters(values):
    """Format validated values as an ARM parameters file for az deployment group."""
    return {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#',
        'contentVersion': '1.0.0.0',
        'parameters': {
            parameter: {'value': values[name].strip()}
            for name, (parameter, _) in SETTINGS.items()
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='path for the ARM parameters file')
    options = parser.parse_args(argv)
    values = {name: os.environ.get(name, '') for name in SETTINGS}
    found = problems(values)
    if found:
        for message in found:
            print(f'::error::API runtime settings: {message}', file=sys.stderr)
        print('Refusing to deploy an API with missing or placeholder Entra/SQL settings.',
              file=sys.stderr)
        return 1
    options.output.write_text(json.dumps(arm_parameters(values), sort_keys=True) + '\n',
                              encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
