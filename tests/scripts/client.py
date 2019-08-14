import argparse
import asyncio
import json
import functools
import time
from http.client import HTTPConnection

import aiohttp

from data import ImportDataGenerator


class CitizensRestApiClient:
    def __init__(self, host='127.0.0.1', port=8080, timeout=10):
        self._host = host
        self._port = port
        self._timeout = timeout

    async def async_http_request(self, http_method='GET', uri='/', body=None):
        t1 = time.time()
        target_host = '{0}:{1}'.format(self._host, self._port)
        async with aiohttp.ClientSession() as session:
            url = f'http://{target_host}{uri}'
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

    async def import_data(self, num_citizens=10000):
        generator = ImportDataGenerator()
        data = json.dumps(list(generator.generate_import_data(num_citizens)))
        requests = []
        for _ in range(10):
            requests.append(
                asyncio.create_task(self.async_http_request('POST', '/imports', body=data))
            )
        responses = await asyncio.gather(*requests)
        return responses

    def import_and_break_connection(self):
        generator = ImportDataGenerator()
        data = json.dumps(list(generator.generate_import_data(num_citizens=30000)))
        connection = HTTPConnection(host, port)
        connection.request('POST', '/imports', json.dumps(data))
        connection.close()
        # TODO: пойти на сервер и убедиться, что все записи вставились


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Citizens REST API Test Client")
    parser.add_argument('--host')
    parser.add_argument('--port')
    args = parser.parse_args()
    host = args.host
    port = args.port or (host and 80) or None

    client = CitizensRestApiClient(host=host, port=port)
    t1 = time.time()

    responses = asyncio.run(client.import_data())
    print('Requests duration: {0}'.format(time.time() - t1))
    print(responses)

    # client.import_and_break_connection()
