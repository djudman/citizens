import json

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestImport(CitizensApiTestCase):
    @unittest_run_loop
    async def test_update_citizen(self):
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

        new_data = {
            'apartment': 777,
            'birth_date': '18.04.1997',
            'relatives': [],
        }
        status, data = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 200)
        self.assertIsNotNone(data)
        self.assertIn('data', data)
        citizen = data['data']
        self.assertIsInstance(citizen, dict)

        self.assertEquals(citizen['citizen_id'], 1)
        self.assertEquals(citizen['apartment'], 777)
        self.assertEquals(citizen['birth_date'], '18.04.1997')
        self.assertEquals(citizen['relatives'], [])
        self.assertEquals(citizen['gender'], 'male')

        citizens = self.app.storage.get_citizens(import_id)
        citizens = sorted(citizens, key=lambda x: x['citizen_id'])  # для удобства тестирования
        self.assertEquals(citizens[0]['citizen_id'], 1)
        self.assertEquals(citizens[0]['apartment'], 777)
        self.assertEquals(citizens[0]['birth_date'], '18.04.1997')
        self.assertEquals(len(citizens[0]['relatives']), 0)

        self.assertEquals(citizens[1]['citizen_id'], 2)
        self.assertEquals(citizens[1]['apartment'], 8)
        self.assertEquals(citizens[1]['birth_date'], '07.05.1987')
        self.assertEquals(len(citizens[1]['relatives']), 0)

