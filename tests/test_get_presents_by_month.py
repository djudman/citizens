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
    async def test_get_presents_by_month(self):
        import_data = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "17.04.1997",
                "gender": "male",
                "relatives": [2, 3]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Иванов Иван Иванович",
                "birth_date": "07.05.1987",
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
                "birth_date": "17.01.1987",
                "gender": "male",
                "relatives": [1]
            }
        ]
        response = await self.client.request('POST', '/imports',
            data=json.dumps(import_data))
        data = await response.json()
        import_id = data['data']['import_id']
        response = await self.client.request('GET',
            f'/imports/{import_id}/citizens/birthdays',
            data=json.dumps(import_data))
        data = await response.json()

        self.assertEquals(len(data['data']['1']), 1)
        citizen = data['data']['1'][0]
        self.assertEquals(citizen['citizen_id'], 1)
        self.assertEquals(citizen['presents'], 1)

        self.assertEquals(len(data['data']['2']), 0)
        self.assertEquals(len(data['data']['3']), 0)

        self.assertEquals(len(data['data']['4']), 2)
        citizen = data['data']['4'][0]
        self.assertEquals(citizen['citizen_id'], 2)
        self.assertEquals(citizen['presents'], 1)
        citizen = data['data']['4'][1]
        self.assertEquals(citizen['citizen_id'], 3)
        self.assertEquals(citizen['presents'], 1)

        self.assertEquals(len(data['data']['5']), 1)
        citizen = data['data']['5'][0]
        self.assertEquals(citizen['citizen_id'], 1)
        self.assertEquals(citizen['presents'], 1)

        for month in range(6, 13):
            self.assertEquals(len(data['data'][str(month)]), 0)
