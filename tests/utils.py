import json
from json.decoder import JSONDecodeError

from aiohttp.test_utils import AioHTTPTestCase

from citizens.main import create_app
from citizens.storage import MemoryStorage, MongoStorage


class CitizensApiTestCase(AioHTTPTestCase):
    async def get_application(self):
        app = create_app()
        app.storage = MemoryStorage()
        # app.storage = MongoStorage({'db': 'citizens'})
        return app

    async def api_request(self, http_method, uri, data=None):
        if data is not None:
            data = json.dumps(data)
        response = await self.client.request(http_method, uri, data=data)
        response_data = await response.read()
        try:
            if response.status in (200, 201) and response_data:
                response_data = json.loads(response_data)
        except JSONDecodeError as e:
            raise Exception(f'Invalid JSON: {response_data}') from e
        return response.status, response_data

    async def import_data(self, data):
        _, data = await self.api_request('POST', '/imports', data)
        return data['data']['import_id']
