import json
from json.decoder import JSONDecodeError

from aiohttp.test_utils import AioHTTPTestCase

from citizens.main import create_app
from citizens.storage import MemoryStorage


class CitizensApiTestCase(AioHTTPTestCase):
    async def get_application(self):
        app = create_app()
        app.storage = MemoryStorage()
        return app

    async def api_request(self, http_method, uri, data=None):
        if data is not None:
            data = json.dumps(data)
        response = await self.client.request(http_method, uri, data=data)
        data = await response.read()
        try:
            data = json.loads(data) if data else None
        except JSONDecodeError as e:
            raise Exception(f'Invalid JSON: {data}') from e
        return response.status, data

    async def import_data(self, data):
        _, data = await self.api_request('POST', '/imports', data)
        return data['data']['import_id']
