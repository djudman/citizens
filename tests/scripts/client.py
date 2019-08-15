import argparse
import asyncio
import json
import functools
import time
from http.client import HTTPConnection

import aiohttp

from data import ImportDataGenerator


class CitizensRestApiClient:
    def __init__(self, host='127.0.0.1', port=8080):
        self._target_host = f'{host}:{port}'

    async def async_http_request(self, http_method='GET', uri='/', body=None):
        t1 = time.time()
        async with aiohttp.ClientSession() as session:
            url = 'http://{target_host}{uri}'.format(target_host=self._target_host, uri=uri)
            do_request = getattr(session, http_method.lower())
            if body is None:
                do_request = functools.partial(do_request, url)
            else:
                body = body.encode()
                print(url)
                do_request = functools.partial(do_request, url, data=body)
            async with do_request() as resp:
                response_data = await resp.text()
                print('{0} took {1}'.format(response_data, time.time() - t1))
                return resp.status, response_data

    async def import_data(self, num_imports=1, num_citizens=10000):
        t1 = time.time()
        generator = ImportDataGenerator()
        data = json.dumps(list(generator.generate_import_data(num_citizens)))
        requests = []
        for _ in range(num_imports):
            requests.append(
                asyncio.create_task(
                    self.async_http_request('POST', '/imports', body=data)
                )
            )
        responses = await asyncio.gather(*requests)
        duration = time.time() - t1
        print(f'Duration of {num_imports} imports: {duration} sec')
        return responses

    def import_and_break_connection(self, num_citizens=1000):
        print(self._target_host)
        generator = ImportDataGenerator()
        data = json.dumps(list(generator.generate_import_data(num_citizens)))
        print('Data generated.')
        connection = HTTPConnection(self._target_host)
        connection.request('POST', '/imports', data)
        print('Data sent.')
        connection.close()
        print('Connection closed.')
        # TODO: пойти на сервер и убедиться, что все записи вставились


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Citizens REST API Test Client")
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8080)
    args = parser.parse_args()

    host = args.host
    port = args.port
    if host != '127.0.0.1':
        port = 80

    client = CitizensRestApiClient(host=host, port=port)
    ############################################################################

    print(asyncio.run(client.import_data(num_imports=2)))
    # client.import_and_break_connection(num_citizens=30000)
