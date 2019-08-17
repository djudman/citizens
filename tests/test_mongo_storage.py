import asyncio
import unittest

from citizens.storage import AsyncMongoStorage, CitizenNotFoundError, CitizensImportNotFound


def run_loop(coro):
    def wrapper(self):
        return self._loop.run_until_complete(coro(self))
    return wrapper


class TestMongoStorage(unittest.TestCase):
    def setUp(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        db_name = 'test_citizens'
        self.storage = AsyncMongoStorage({
            'connection_string': 'mongodb://localhost:27017',
            'db': db_name,
        })
        db = self.storage._driver.get_database(db_name)
        for name in db.list_collection_names():
            db.drop_collection(name)

    def tearDown(self):
        self._loop.run_until_complete(self.storage.close())

    @run_loop
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
        import_id = await self.storage.import_citizens([data])
        dataBefore = list(await self.storage.get_citizens(import_id, {'citizen_id': 3}))
        dataBefore = dataBefore[0]
        new_values = {'name': 'Tom', 'street': 'Lenina', 'relatives': [3]}
        await self.storage.update_citizen(import_id, 3, new_values)
        dataAfter = list(await self.storage.get_citizens(import_id, {'citizen_id': 3}))
        dataAfter = dataAfter[0]
        self.assertNotEqual(dataBefore['name'], dataAfter['name'])
        self.assertNotEqual(dataBefore['street'], dataAfter['street'])
        self.assertNotEqual(dataBefore['relatives'], dataAfter['relatives'])
        equalFields = ('town', 'building', 'apartment', 'birth_date', 'gender')
        for field in equalFields:
            self.assertEqual(dataBefore[field], dataAfter[field])

    @run_loop
    async def test_import(self):
        import_id = await self.storage.import_citizens([{
            'citizen_id': 3,
            'town': 'NY',
            'street': '',
            'building': '1b',
            'apartment': 202,
            'name': 'Bob',
            'birth_date': '21.12.2012',
            'gender': 'male',
            'relatives': [],
        }])
        all_citizens_after = list(await self.storage.get_citizens(import_id))
        self.assertEqual(len(all_citizens_after), 1)

    @run_loop
    async def test_import_does_not_exists(self):
        with self.assertRaises(CitizensImportNotFound) as ctx:
            _ = list(await self.storage.get_citizens(999))
        self.assertEquals(str(ctx.exception), 'Import `999` does not exists.')
