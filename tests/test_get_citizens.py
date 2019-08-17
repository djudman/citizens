import json

from aiohttp.test_utils import unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestGetCitizens(CitizensApiTestCase):
    @unittest_run_loop
    async def test_get_citizens(self):
        import_id = await self.import_data([
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
        ])
        status, data = await self.api_request('GET', f'/imports/{import_id}/citizens')
        self.assertEquals(status, 200)
        self.assertIsNotNone(data)
        self.assertIn('data', data)

        citizens = data['data']
        self.assertIsInstance(citizens, list)
        self.assertEquals(len(citizens), 2)

        self.assertEquals(citizens[0]['citizen_id'], 1)
        self.assertEquals(citizens[0]['apartment'], 7)
        self.assertEquals(citizens[0]['birth_date'], '17.04.1997')
        self.assertEquals(len(citizens[0]['relatives']), 1)

        self.assertEquals(citizens[1]['citizen_id'], 2)
        self.assertEquals(citizens[1]['apartment'], 8)
        self.assertEquals(citizens[1]['birth_date'], '07.05.1987')
        self.assertEquals(len(citizens[1]['relatives']), 1)

    @unittest_run_loop
    async def test_import_does_not_exists(self):
        import_id = 100
        status, _ = await self.api_request('GET', f'/imports/{import_id}/citizens')
        self.assertEquals(status, 400)
