from aiohttp.test_utils import unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestImport(CitizensApiTestCase):
    @unittest_run_loop
    async def test_save_import(self):
        citizens = [
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
        status, data = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 201)
        self.assertIsNotNone(data)
        self.assertIn('data', data)
        self.assertIn('import_id', data['data'])
        import_id = data['data']['import_id']
        self.assertIsNotNone(import_id)
        self.assertIsInstance(import_id, int)

        citizens = list(await self.app.storage.get_citizens(import_id))
        self.assertEqual(citizens[0]['citizen_id'], 1)
        self.assertEqual(citizens[0]['name'], 'Иванов Сергей Иванович')

        self.assertEqual(citizens[1]['citizen_id'], 2)
        self.assertEqual(citizens[1]['name'], 'Иванов Иван Иванович')

    @unittest_run_loop
    async def test_birth_date_invalid_format(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "17-04-1997",
                "gender": "male",
                "relatives": []
            },
        ]
        status, _ = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_birth_date_is_not_exists(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "30.02.1997",
                "gender": "male",
                "relatives": []
            },
        ]
        status, _ = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_relative_not_found_in_import(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": [2]
            },
        ]
        status, _ = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_relative_is_not_mutual(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": [2]
            },
            {
                "citizen_id": 2,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "02.02.1997",
                "gender": "male",
                "relatives": [3]
            },
        ]
        status, _ = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_not_unique_citizen_id(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": []
            },
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 8,
                "name": "Иванов Сергей Иванович",
                "birth_date": "02.02.1997",
                "gender": "male",
                "relatives": []
            }
        ]
        status, _ = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_empty_input_data(self):
        status, _ = await self.api_request('POST', '/imports', {})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_redundant_field(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                "relatives": [],
                "one_more_field": 1,
            },
        ]
        status, _ = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_no_field(self):
        citizens = [
            {
                "citizen_id": 1,
                "town": "Москва",
                "street": "Льва Толстого",
                "building": "16к7стр5",
                "apartment": 7,
                "name": "Иванов Сергей Иванович",
                "birth_date": "01.02.1997",
                "gender": "male",
                # "relatives": [],
            },
        ]
        status, _ = await self.api_request('POST', '/imports', {'citizens': citizens})
        self.assertEqual(status, 400)
