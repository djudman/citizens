import asyncio
import unittest

from aiohttp.test_utils import unittest_run_loop

from citizens.storage import AsyncMongoStorage, CitizenNotFoundError
from tests.utils import CitizensApiTestCase


class TestAsyncStorage(CitizensApiTestCase):
    def setUp(self):
        super().setUp()
        self.storage = AsyncMongoStorage({
            'host': 'localhost',
            'db': 'test_citizens',
        })

    def tearDown(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.storage.close())
        super().tearDown()

    @unittest_run_loop
    async def test_generate_import_id(self):
        import_id = await self.storage.generate_import_id()
        self.assertIsInstance(import_id, int)
        self.assertGreater(import_id, 0)

    @unittest_run_loop
    async def test_insert_citizen(self):
        data = {
            'citizen_id': 2,
            'town': 'NY',
            'street': '',
            'building': '1b',
            'apartment': 202,
            'name': 'Bob',
            'birth_date': '21.12.2012',
            'gender': 'male',
            'relatives': [],
        }
        import_id = await self.storage.generate_import_id()
        all_citizens_before = [data async for data in self.storage.get_citizens(import_id)]
        self.assertEqual(len(all_citizens_before), 0)
        await self.storage.insert_citizen(import_id, data)
        all_citizens_after = [data async for data in self.storage.get_citizens(import_id)]
        self.assertEqual(len(all_citizens_after), 1)

    @unittest_run_loop
    async def test_get_one_citizen(self):
        data = {
            'citizen_id': 3,
            'town': 'NY',
            'street': '',
            'building': '1b',
            'apartment': 202,
            'name': 'Bob',
            'birth_date': '21.12.2012',
            'gender': 'male',
            'relatives': [],
        }
        import_id = await self.storage.generate_import_id()
        with self.assertRaises(CitizenNotFoundError):
            await self.storage.get_one_citizen(import_id, 3)
        await self.storage.insert_citizen(import_id, data)
        data = await self.storage.get_one_citizen(import_id, 3)
        self.assertIsNotNone(data)
        self.assertEqual(data['citizen_id'], 3)
        self.assertEqual(data['name'], 'Bob')

    @unittest_run_loop
    async def test_update_citizen(self):
        data = {
            'citizen_id': 3,
            'town': 'NY',
            'street': '',
            'building': '1b',
            'apartment': 202,
            'name': 'Bob',
            'birth_date': '21.12.2012',
            'gender': 'male',
            'relatives': [],
        }
        import_id = await self.storage.generate_import_id()
        await self.storage.insert_citizen(import_id, data)
        dataBefore = await self.storage.get_one_citizen(import_id, 3)
        new_values = {'name': 'Tom', 'street': 'Lenina', 'relatives': [3]}
        await self.storage.update_citizen(import_id, 3, new_values)
        dataAfter = await self.storage.get_one_citizen(import_id, 3)
        self.assertNotEqual(dataBefore['name'], dataAfter['name'])
        self.assertNotEqual(dataBefore['street'], dataAfter['street'])
        self.assertNotEqual(dataBefore['relatives'], dataAfter['relatives'])
        equalFields = ('town', 'building', 'apartment', 'birth_date', 'gender')
        for field in equalFields:
            self.assertEqual(dataBefore[field], dataAfter[field])
