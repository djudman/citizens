import argparse
import json
import os
import sys
from os.path import dirname, realpath, join

sys.path.append(dirname(dirname(dirname(dirname(realpath(__file__))))))

from tests.scripts.data import ImportDataGenerator


def create_ammo(target_host='localhost', num_imports=3, num_citizens_per_import=3,
                filename='ammo.txt'):
    generator = ImportDataGenerator()
    imports = (generator.generate_import_data(num_citizens_per_import)
               for _ in range(num_imports))
    requests = []
    for import_data in imports:
        str_import_data = json.dumps(list(import_data))
        content_length = len(str_import_data)
        headers = '\r\n'.join([
            'POST /imports HTTP/1.1',
            'Content-Length: {0}'.format(content_length),
            'Host: {0}'.format(target_host),
            'User-Agent: yandex-tank'
        ])
        request = '{request_headers}\r\n\r\n{body}'.format(
            request_headers=headers,
            body=str_import_data
        )
        requests.append(
            '{request_size} {tag}\n{request}'.format(
                request_size=len(request),
                tag='import',
                request=request
            )
        )
    with open(filename, 'w') as f:
        f.write('\n'.join(requests))
    return filename


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ammo generator for yandex-tank')
    parser.add_argument('--host')
    args = parser.parse_args()
    if not args.host:
        print('Host is not specified. Use `--host` option to specify host.')
        sys.exit(1)
    create_ammo(
        target_host=args.host,
        num_imports=10,
        num_citizens_per_import=10000,
        filename=join(realpath(dirname(__file__)), 'ammo.txt')
    )
