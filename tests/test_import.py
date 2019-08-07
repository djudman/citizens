from aiohttp.test_utils import unittest_run_loop

from tests.utils import CitizensApiTestCase


class TestImport(CitizensApiTestCase):
    @unittest_run_loop
    async def test_save_import(self):
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
        status, data = await self.api_request('POST', '/imports', import_data)
        self.assertEquals(status, 201)
        self.assertIsNotNone(data)
        self.assertIn('data', data)
        self.assertIn('import_id', data['data'])
        import_id = data['data']['import_id']
        self.assertIsNotNone(import_id)
        self.assertIsInstance(import_id, int)

        citizens = self.app.storage.get_citizens(import_id)
        self.assertEquals(citizens[0]['citizen_id'], 1)
        self.assertEquals(citizens[0]['name'], 'Иванов Сергей Иванович')

        self.assertEquals(citizens[1]['citizen_id'], 2)
        self.assertEquals(citizens[1]['name'], 'Иванов Иван Иванович')

    @unittest_run_loop
    async def test_birth_date_invalid_format(self):
        import_data = [
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
        status, data = await self.api_request('POST', '/imports', import_data)
        self.assertEquals(status, 400)
        self.assertIsNone(data)

    @unittest_run_loop
    async def test_birth_date_is_not_exists(self):
        import_data = [
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
        status, data = await self.api_request('POST', '/imports', import_data)
        self.assertEquals(status, 400)
        self.assertIsNone(data)

    @unittest_run_loop
    async def test_relative_not_found_in_import(self):
        import_data = [
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
        status, data = await self.api_request('POST', '/imports', import_data)
        self.assertEquals(status, 400)
        self.assertIsNone(data)

    @unittest_run_loop
    async def test_relative_is_not_mutual(self):
        import_data = [
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
        status, data = await self.api_request('POST', '/imports', import_data)
        self.assertEquals(status, 400)
        self.assertIsNone(data)

    @unittest_run_loop
    async def test_not_unique_citizen_id(self):
        import_data = [
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
        status, data = await self.api_request('POST', '/imports', import_data)
        self.assertEquals(status, 400)
        self.assertIsNone(data)


    # TODO: test_town_is_empty
    # TODO: test_street_is_empty
    # TODO: test_building_is_empty
    # TODO: test_apartment_is_not_number
    # TODO: test_name_is_empty
    # TODO: test_gender_invalid_value
    # TODO: test_self_in_relatives
