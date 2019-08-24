import datetime
import json

from aiohttp.test_utils import unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestGetAgePercentiles(CitizensApiTestCase):
    def setUp(self):
        super().setUp()
        self._counter = 1

    def _make_citizen_data(self, town, age):
        today = datetime.datetime.utcnow().date()
        birth_date = datetime.date(year=(today.year - age), month=today.month, day=today.day)
        data = {
            'citizen_id': self._counter,
            'town': town,
            'street': 'Ленина',
            'building': '1',
            'apartment': 1,
            'name': 'Иванов',
            'birth_date': birth_date.strftime('%d.%m.%Y'),
            'gender': 'male',
            'relatives': [],
        }
        self._counter += 1
        return data

    @unittest_run_loop
    async def test_get_percentiles(self):
        citizens = [
            self._make_citizen_data('Москва', 15),
            self._make_citizen_data('Москва', 20),
            self._make_citizen_data('Москва', 62),
            self._make_citizen_data('Санкт-Петербург', 5),
            self._make_citizen_data('Санкт-Петербург', 32),
            self._make_citizen_data('Санкт-Петербург', 32),
            self._make_citizen_data('Санкт-Петербург', 59),
            self._make_citizen_data('Санкт-Петербург', 65),
        ]
        import_id = await self.import_data(citizens)
        status, data = await self.api_request(
            'GET', f'/imports/{import_id}/towns/stat/percentile/age')
        self.assertEqual(status, 200)
        self.assertIsNotNone(data)
        self.assertIn('data', data)

        stat = data['data']
        self.assertIsInstance(stat, list)
        self.assertEqual(len(stat), 2)

        self.assertEqual(stat[0]['town'], 'Москва')
        self.assertEqual(stat[0]['p50'], 20)
        self.assertEqual(stat[0]['p75'], 41)
        self.assertEqual(stat[0]['p99'], 61.16)

        self.assertEqual(stat[1]['town'], 'Санкт-Петербург')
        self.assertEqual(stat[1]['p50'], 32)
        self.assertEqual(stat[1]['p75'], 59)
        self.assertEqual(stat[1]['p99'], 64.76)

    @unittest_run_loop
    async def test_import_does_not_exists(self):
        import_id = 100
        status, _ = await self.api_request(
            'GET', f'/imports/{import_id}/towns/stat/percentile/age')
        self.assertEqual(status, 400)
