import json

from aiohttp.test_utils import unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestGetPresentsByMonth(CitizensApiTestCase):
    @unittest_run_loop
    async def test_self_present(self):
        import_id = await self.import_data([
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иван",
                "birth_date": "17.06.1997",
                "gender": "male",
                "relatives": [1]
            }
        ])
        status, data = await self.api_request(
            'GET', f'/imports/{import_id}/citizens/birthdays')
        self.assertEquals(status, 200)

        presents_by_month = data['data']
        stat = presents_by_month['6']
        self.assertEquals(len(stat), 1)
        self.assertEquals(stat[0]['citizen_id'], 1)
        self.assertEquals(stat[0]['presents'], 1)

        empty_months = [str(i + 1) for i in range(12) if (i + 1) != 6]
        for month in empty_months:
            self.assertIn(month, presents_by_month)
            self.assertIsInstance(presents_by_month[month], list)
            self.assertEqual(len(presents_by_month[month]), 0)

    @unittest_run_loop
    async def test_multiple_presents_same_month(self):
        import_id = await self.import_data([
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иван",
                "birth_date": "17.06.1997",
                "gender": "male",
                "relatives": [2, 3]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Василий",
                "birth_date": "07.03.1987",
                "gender": "male",
                "relatives": [1]
            },
            {
                "citizen_id": 3,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Петр",
                "birth_date": "17.03.1987",
                "gender": "male",
                "relatives": [1]
            }
        ])
        status, data = await self.api_request(
            'GET', f'/imports/{import_id}/citizens/birthdays')
        self.assertEquals(status, 200)

        presents_by_month = data['data']
        stat = presents_by_month['3']
        self.assertEquals(len(stat), 1)
        self.assertEquals(stat[0]['citizen_id'], 1)
        self.assertEquals(stat[0]['presents'], 2)

    @unittest_run_loop
    async def test_citizen_birthdays(self):
        import_id = await self.import_data([
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иван",
                "birth_date": "17.04.1997",
                "gender": "male",
                "relatives": [3, 4]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Василий",
                "birth_date": "07.05.1987",
                "gender": "male",
                "relatives": [3]
            },
            {
                "citizen_id": 3,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Петр",
                "birth_date": "17.01.1987",
                "gender": "male",
                "relatives": [1, 2]
            },
            {
                "citizen_id": 4,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Дмитрий",
                "birth_date": "01.01.1987",
                "gender": "male",
                "relatives": [1, 4]
            }
        ])
        status, data = await self.api_request(
            'GET', f'/imports/{import_id}/citizens/birthdays')
        self.assertEquals(status, 200)
        self.assertIsNotNone(data)
        self.assertIn('data', data)

        presents_by_month = data['data']
        self.assertIsInstance(presents_by_month, dict)

        for i in range(12):
            month = str(i + 1)
            self.assertIn(month, presents_by_month)

        stat = sorted(presents_by_month['1'], key=lambda data: data['citizen_id'])
        self.assertEquals(len(stat), 3)
        self.assertEquals(stat[0]['citizen_id'], 1)
        self.assertEquals(stat[0]['presents'], 2)
        self.assertEquals(stat[1]['citizen_id'], 2)
        self.assertEquals(stat[1]['presents'], 1)
        self.assertEquals(stat[2]['citizen_id'], 4)
        self.assertEquals(stat[2]['presents'], 1)

        self.assertEquals(len(presents_by_month['2']), 0)
        self.assertEquals(len(presents_by_month['3']), 0)

        stat = sorted(presents_by_month['4'], key=lambda data: data['citizen_id'])
        self.assertEquals(len(stat), 2)
        self.assertEquals(stat[0]['citizen_id'], 3)
        self.assertEquals(stat[0]['presents'], 1)
        self.assertEquals(stat[1]['citizen_id'], 4)
        self.assertEquals(stat[1]['presents'], 1)

        stat = sorted(presents_by_month['5'], key=lambda data: data['citizen_id'])
        self.assertEquals(len(stat), 1)
        self.assertEquals(stat[0]['citizen_id'], 3)
        self.assertEquals(stat[0]['presents'], 1)

        for month in range(6, 13):
            self.assertEquals(len(presents_by_month[str(month)]), 0)

    @unittest_run_loop
    async def test_import_does_not_exists(self):
        import_id = 100
        status, _ = await self.api_request('GET', f'/imports/{import_id}/citizens/birthdays')
        self.assertEquals(status, 400)
