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

    # TODO: test invalid data cases
