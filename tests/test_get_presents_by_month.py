import json

from aiohttp.test_utils import unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestImport(CitizensApiTestCase):
    @unittest_run_loop
    async def test_get_presents_by_month(self):
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
        ])
        status, data = await self.api_request('GET', f'/imports/{import_id}/citizens/birthdays')
        self.assertEquals(status, 200)
        self.assertIsNotNone(data)
        self.assertIn('data', data)

        presents_by_month = data['data']
        self.assertIsInstance(presents_by_month, dict)

        self.assertEquals(len(presents_by_month['1']), 1)
        citizen = presents_by_month['1'][0]
        self.assertEquals(citizen['citizen_id'], 1)
        self.assertEquals(citizen['presents'], 1)

        self.assertEquals(len(presents_by_month['2']), 0)
        self.assertEquals(len(presents_by_month['3']), 0)

        self.assertEquals(len(presents_by_month['4']), 2)
        citizen = presents_by_month['4'][0]
        self.assertEquals(citizen['citizen_id'], 2)
        self.assertEquals(citizen['presents'], 1)
        citizen = presents_by_month['4'][1]
        self.assertEquals(citizen['citizen_id'], 3)
        self.assertEquals(citizen['presents'], 1)

        self.assertEquals(len(presents_by_month['5']), 1)
        citizen = presents_by_month['5'][0]
        self.assertEquals(citizen['citizen_id'], 1)
        self.assertEquals(citizen['presents'], 1)

        for month in range(6, 13):
            self.assertEquals(len(presents_by_month[str(month)]), 0)
