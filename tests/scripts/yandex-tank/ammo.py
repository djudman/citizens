import argparse
import json
import os
import random
import sys
from os.path import dirname, realpath, join

sys.path.append(dirname(dirname(dirname(dirname(realpath(__file__))))))

from tests.scripts.data import ImportDataGenerator


def create_ammo(target_host='localhost', num_imports=3, num_citizens_per_import=3,
                filename='ammo.txt'):
    generator = ImportDataGenerator()
    imports = (generator.generate_import_data(num_citizens_per_import)
               for _ in range(num_imports))

    import_requests = []
    requests = []
    for index, import_data in enumerate(imports):
        import_id = index + 1
        import_request = create_import_request(target_host, import_data)
        import_requests.append(import_request)
        for _ in range(num_citizens_per_import // 2):
            r = create_patch_citizen_request(target_host, import_id, num_citizens_per_import)
            requests.append(r)
        for _ in range(num_citizens_per_import // 4):
            r = create_get_all_citizens_request(target_host, import_id)
            requests.append(r)
        for _ in range(num_citizens_per_import // 4):
            r = create_get_birthdays_request(target_host, import_id)
            requests.append(r)
        for _ in range(num_citizens_per_import // 3):
            r = create_get_percentiles_request(target_host, import_id)
            requests.append(r)
        random.shuffle(requests)
    for i, r in enumerate(import_requests):
        requests.insert(i, r)

    with open(filename, 'w') as f:
        f.write('\n'.join(requests))
    return filename


def create_http_request(target_host, method, uri, data=None, tag='request'):
    str_data = json.dumps(data) if data is not None else ''
    content_length = len(str_data)
    headers = '\r\n'.join([
        '{0} {1} HTTP/1.1'.format(method, uri),
        'Content-Length: {0}'.format(content_length),
        'Host: {0}'.format(target_host),
        'User-Agent: yandex-tank'
    ])
    request = '{request_headers}\r\n\r\n{body}'.format(
        request_headers=headers,
        body=str_data
    )
    return '{request_size} {tag}\n{request}'.format(
        request_size=len(request),
        tag=tag,
        request=request
    )


def create_import_request(target_host, import_data):
    return create_http_request(
        target_host,
        method='POST',
        uri='/imports',
        data=list(import_data),
        tag='import'
    )


def create_patch_citizen_request(target_host, import_id, num_citizens):
    citizen_id = random.randint(2, num_citizens)
    new_values = {
        'name': 'Updated',
        'relatives': [random.randint(1, num_citizens)]
    }
    patch_citizen_request = create_http_request(
        target_host,
        method='PATCH',
        uri=f'/imports/{import_id}/citizens/{citizen_id}',
        data=new_values,
        tag='patch_citizen'
    )
    return patch_citizen_request


def create_get_all_citizens_request(target_host, import_id):
    return create_http_request(
        target_host,
        method='GET',
        uri=f'/imports/{import_id}/citizens',
        tag='get_all_citizens'
    )


def create_get_birthdays_request(target_host, import_id):
    return create_http_request(
        target_host,
        method='GET',
        uri=f'/imports/{import_id}/citizens/birthdays',
        tag='get_birthdays'
    )


def create_get_percentiles_request(target_host, import_id):
    return create_http_request(
        target_host,
        method='GET',
        uri=f'/imports/{import_id}/towns/stat/percentile/age',
        tag='get_percentiles'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ammo generator for yandex-tank')
    parser.add_argument('--host')
    args = parser.parse_args()
    if not args.host:
        print('Host is not specified. Use `--host` option to specify host.')
        sys.exit(1)
    create_ammo(
        target_host=args.host,
        num_imports=2,
        num_citizens_per_import=10000,
        filename=join(realpath(dirname(__file__)), 'ammo.txt')
    )
