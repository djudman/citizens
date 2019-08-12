import asyncio
import json
import functools
import time

import aiohttp

from data import ImportDataGenerator


class CitizensRestApiClient:
    def __init__(self, timeout=10):
        self._timeout = timeout

    async def async_http_request(self, target_host, http_method='GET', uri='/', body=None):
        t1 = time.time()
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

    async def import_data(self):
        generator = ImportDataGenerator()
        data = json.dumps(list(generator.generate_import_data(num_citizens=10000)))
        requests = []
        for _ in range(10):
            requests.append(
                asyncio.create_task(self.async_http_request('127.0.0.1:8080', 'POST', '/imports', body=data))
            )
        responses = await asyncio.gather(*requests)
        return responses


if __name__ == '__main__':
    client = CitizensRestApiClient()
    t1 = time.time()
    responses = asyncio.run(client.import_data())
    print('Requests duration: {0}'.format(time.time() - t1))
    print(responses)
