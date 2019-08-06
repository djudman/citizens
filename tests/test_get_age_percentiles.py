from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import json

from citizens.main import get_app
from citizens.storage import MemoryStorage


class TestImport(AioHTTPTestCase):
    async def get_application(self):
        app = get_app()
        app.storage = MemoryStorage()
        return app

    @unittest_run_loop
    async def test_get_citizen(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "17.04.1999",
                "gender": "male",
                "relatives": [2]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Иванов Иван Иванович",
                "birth_date": "07.05.1989",
                "gender": "male",
                "relatives": [1]
            },
            {
                "citizen_id": 3,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Иванов Иван Иванович",
                "birth_date": "07.05.1979",
                "gender": "male",
                "relatives": []
            },
            {
                "citizen_id": 4,
                "town": "Санкт-Петербург",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Иванов Иван Иванович",
                "birth_date": "07.05.1949",
                "gender": "male",
                "relatives": []
            },
            {
                "citizen_id": 4,
                "town": "Санкт-Петербург",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Иванов Иван Иванович",
                "birth_date": "07.05.1959",
                "gender": "male",
                "relatives": []
            }
        ]
        response = await self.client.request('POST', '/imports',
            data=json.dumps(import_data))
        data = await response.json()
        import_id = data['data']['import_id']
        response = await self.client.request('GET', f'/imports/{import_id}/towns/stat/percentile/age')
        data = await response.json()
        self.assertEquals(len(data['data']), 2)
        self.assertEquals(data['data'][0]['town'], 'Москва')
        self.assertEquals(data['data'][0]['p50'], 30)
        self.assertEquals(data['data'][0]['p75'], 35)
        self.assertEquals(data['data'][0]['p99'], 39)

        self.assertEquals(data['data'][1]['town'], 'Санкт-Петербург')
        self.assertEquals(data['data'][1]['p50'], 65)
        self.assertEquals(data['data'][1]['p75'], 67)
        self.assertEquals(data['data'][1]['p99'], 69)
