from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import json

from citizens.api import new_import
from citizens.main import get_app
from citizens.storage import MemoryStorage


class TestImport(AioHTTPTestCase):
    async def get_application(self):
        app = get_app()
        app.storage = MemoryStorage()
        return app

    @unittest_run_loop
    async def test_update_citizen(self):
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
                "relatives": [2]
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
            }
        ]
        response = await self.client.request('POST', '/imports',
            data=json.dumps(import_data))
        data = await response.json()
        import_id = data['data']['import_id']
        new_data = {
            'apartment': 777,
            'birth_date': '18.04.1997',
            'relatives': [],
        }
        response = await self.client.request('PATCH',
            f'/imports/{import_id}/citizens/1', data=json.dumps(new_data))
        self.assertEquals(response.status, 200)
        data = await response.json()
        citizens = self.app.storage.get_citizens(import_id)
        citizens = sorted(citizens, key=lambda x: x['citizen_id'])
        self.assertEquals(citizens[0]['citizen_id'], 1)
        self.assertEquals(citizens[0]['apartment'], 777)
        self.assertEquals(citizens[0]['birth_date'], '18.04.1997')
        self.assertEquals(len(citizens[0]['relatives']), 0)

        self.assertEquals(citizens[1]['citizen_id'], 2)
        self.assertEquals(citizens[1]['apartment'], 8)
        self.assertEquals(citizens[1]['birth_date'], '07.05.1987')
        self.assertEquals(len(citizens[1]['relatives']), 0)

