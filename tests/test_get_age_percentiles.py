import json

from aiohttp.test_utils import unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestGetAgePercentiles(CitizensApiTestCase):
    @unittest_run_loop
    async def test_get_percentiles(self):
        import_id = await self.import_data([
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
                "citizen_id": 5,
                "town": "Санкт-Петербург",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Иванов Иван Иванович",
                "birth_date": "07.05.1959",
                "gender": "male",
                "relatives": []
            }
        ])
        status, data = await self.api_request('GET', f'/imports/{import_id}/towns/stat/percentile/age')
        self.assertEquals(status, 200)
        self.assertIsNotNone(data)
        self.assertIn('data', data)

        stat = data['data']
        self.assertIsInstance(stat, list)
        self.assertEquals(len(stat), 2)

        self.assertEquals(stat[0]['town'], 'Москва')
        self.assertEquals(stat[0]['p50'], 30)
        self.assertEquals(stat[0]['p75'], 35)
        self.assertEquals(stat[0]['p99'], 39)

        self.assertEquals(stat[1]['town'], 'Санкт-Петербург')
        self.assertEquals(stat[1]['p50'], 65)
        self.assertEquals(stat[1]['p75'], 67)
        self.assertEquals(stat[1]['p99'], 69)
