import json

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestUpdateCitizen(CitizensApiTestCase):
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
        response_data = data['data']
        self.assertIsInstance(response_data, dict)

        self.assertEquals(response_data['citizen_id'], 1)
        self.assertEquals(response_data['apartment'], 777)
        self.assertEquals(response_data['birth_date'], '18.04.1997')
        self.assertEquals(response_data['relatives'], [])
        self.assertEquals(response_data['gender'], 'male')

        citizens = list(await self.app.storage.get_citizens(import_id))
        citizens = sorted(citizens, key=lambda x: x['citizen_id'])  # для удобства тестирования
        self.assertEquals(citizens[0]['citizen_id'], 1)
        self.assertEquals(citizens[0]['apartment'], 777)
        self.assertEquals(citizens[0]['birth_date'], '18.04.1997')
        self.assertEquals(len(citizens[0]['relatives']), 0)

        self.assertEquals(citizens[1]['citizen_id'], 2)
        self.assertEquals(citizens[1]['apartment'], 8)
        self.assertEquals(citizens[1]['birth_date'], '07.05.1987')
        self.assertEquals(len(citizens[1]['relatives']), 0)

    @unittest_run_loop
    async def test_update_relatives(self):
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
                "relatives": []
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
                "relatives": []
            }
        ])

        new_data = {
            'relatives': [2],
        }
        status, data = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 200)
        response_data = data['data']
        self.assertEqual(response_data['relatives'], [2])
        citizens = list(await self.app.storage.get_citizens(import_id))
        self.assertEquals(citizens[0]['citizen_id'], 1)
        self.assertEquals(citizens[0]['relatives'], [2])
        self.assertEquals(citizens[1]['citizen_id'], 2)
        self.assertEquals(citizens[1]['relatives'], [1])

    @unittest_run_loop
    async def test_birth_date_invalid_format(self):
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
                "relatives": []
            }
        ])

        new_data = {
            'apartment': 777,
            'birth_date': '18/04/1997',
        }
        status, data = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 400)

    @unittest_run_loop
    async def test_not_mutual_relatives(self):
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
                "relatives": []
            }
        ])

        new_data = {
            'relatives': [2],
        }
        status, data = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 400)

    @unittest_run_loop
    async def test_self_in_relatives(self):
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
                "relatives": []
            }
        ])

        new_data = {
            'relatives': [1],
        }
        status, data = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 200)
        self.assertEquals(data['data']['relatives'], [1])


    @unittest_run_loop
    async def test_update_citizen_id(self):
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
                "relatives": []
            }
        ])
        new_data = {
            'citizen_id': 2,
            'name': 'Алексей',
        }
        status, _ = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 400)

    @unittest_run_loop
    async def test_update_not_existent_citizen(self):
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
                "relatives": []
            }
        ])
        new_data = {
            'name': 'Алексей',
        }
        status, _ = await self.api_request('PATCH', f'/imports/{import_id}/citizens/2', new_data)
        self.assertEquals(status, 400)
    
    @unittest_run_loop
    async def test_set_empty_name(self):
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
                "relatives": []
            }
        ])
        new_data = {
            'name': '',
        }
        status, _ = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 400)

    @unittest_run_loop
    async def test_set_invalid_field(self):
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
                "relatives": []
            }
        ])
        new_data = {
            'xxx': 'xxx',
        }
        status, _ = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 400)

    @unittest_run_loop
    async def test_no_new_values(self):
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
                "relatives": []
            }
        ])
        new_data = {}
        status, _ = await self.api_request('PATCH', f'/imports/{import_id}/citizens/1', new_data)
        self.assertEquals(status, 400)
