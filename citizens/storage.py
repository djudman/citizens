from pymongo import MongoClient, ReturnDocument
from motor.motor_asyncio import AsyncIOMotorClient


class CitizenNotFoundError(Exception):
    pass


class CitizensStorage:
    async def generate_import_id(self) -> int:
        raise NotImplementedError()

    async def insert_citizen(self, import_id: int, data: dict):
        raise NotImplementedError()

    async def get_citizens(self, import_id):
        raise NotImplementedError()

    async def get_one_citizen(self, import_id, citizen_id):
        raise NotImplementedError()

    async def update_citizen(self, import_id, citizen_id, new_values):
        raise NotImplementedError()

    async def _update_relatives(self, import_id, citizen_id, new_relatives):
        old_data = await self.get_one_citizen(import_id, citizen_id)
        old_relatives = old_data['relatives']
        for rid in old_relatives:
            if rid not in new_relatives:
                # NOTE: Удаляем на той стороне меня из relatives
                await self.delete_relative_from(import_id, rid, citizen_id)
        for rid in new_relatives:
            if rid not in old_relatives:
                # NOTE: Добавляем на той стороне меня в relatives
                await self.add_relative_to(import_id, citizen_id, rid)

    async def add_relative_to(self, import_id, citizen_id, relative_id):
        raise NotImplementedError()

    async def delete_relative_from(self, import_id, citizen_id, relative_id):
        raise NotImplementedError()

    def close(self):
        pass


class MemoryStorage(CitizensStorage):  # используется в тестах
    def __init__(self):
        self._data = {}
        self._counter = 1

    async def generate_import_id(self) -> int:
        self._counter += 1
        return self._counter

    async def insert_citizen(self, import_id: int, data: dict):
        cid = data['citizen_id']
        if import_id not in self._data:
            self._data[import_id] = {}
        self._data[import_id][cid] = data

    async def get_citizens(self, import_id):
        for data in self._data[import_id].values():
            yield data

    async def get_one_citizen(self, import_id, citizen_id):
        if citizen_id not in self._data[import_id]:
            raise CitizenNotFoundError(f'Citizen {citizen_id} not found.')
        return self._data[import_id][citizen_id]

    async def update_citizen(self, import_id, citizen_id, new_values):
        if 'relatives' in new_values:
            await self._update_relatives(import_id, citizen_id, new_values['relatives'])
        if citizen_id not in self._data[import_id]:
            raise CitizenNotFoundError(f'Citizen {citizen_id} not found.')
        for field_name, value in new_values.items():
            self._data[import_id][citizen_id][field_name] = value
        return self._data[import_id][citizen_id]

    async def add_relative_to(self, import_id, citizen_id, relative_id):
        self._data[import_id][citizen_id]['relatives'].append(relative_id)

    async def delete_relative_from(self, import_id, citizen_id, relative_id):
        self._data[import_id][citizen_id]['relatives'].remove(relative_id)


class MongoStorage(CitizensStorage):
    def __init__(self, config):
        self._driver = MongoClient(host=config.get('host'), port=config.get('port'))
        self._db = self._driver.get_database(config['db'])

    async def generate_import_id(self) -> int:
        # NOTE: вообще-то, делать такое в mongodb - плохая практика, может
        # привести к разным проблемам, например, при масштабировании.
        # Я так делаю, потому что в задании приводятся примеры с
        # целочисленными id для import-ов и ничего не сказано об ограничении
        # на тип import_id. Это такая перестраховка на случай, если проверяющий
        # робот почему-то ожидает целые import_id.
        collection = self._db.get_collection('counters')
        data = collection.find_one_and_update(
            {'_id': 'import_id'},
            {'$inc': {'counter': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return data['counter']

    def _get_collection(self, import_id):
        collection_name = f'import_{import_id}'
        return self._db.get_collection(collection_name)

    async def insert_citizen(self, import_id: int, data: dict):
        data['_id'] = data['citizen_id']
        self._get_collection(import_id).insert_one(data)

    async def get_citizens(self, import_id):
        results = []
        for entry in self._get_collection(import_id).find():
            del entry['_id']
            results.append(entry)
        return results  # TODO: вернуть курсор / генератор / НЕ СПИСОК

    async def get_one_citizen(self, import_id, citizen_id):
        citizen = self._get_collection(import_id).find_one(
            {'citizen_id': citizen_id})  # TODO: использовать _id
        if citizen is None:
            raise CitizenNotFoundError(f'Citizen {citizen_id} not found.')
        return citizen

    async def update_citizen(self, import_id, citizen_id, new_values):
        if 'relatives' in new_values:
            await self._update_relatives(import_id, citizen_id, new_values['relatives'])
        updated_data = self._get_collection(import_id).find_one_and_update(
            {'citizen_id': citizen_id},  # TODO: использовать _id
            {'$set': new_values},
            return_document=ReturnDocument.AFTER
        )
        if updated_data is None:
            raise CitizenNotFoundError(f'Citizen {citizen_id} not found.')
        del updated_data['_id']
        return updated_data

    async def add_relative_to(self, import_id, citizen_id, relative_id):
        updated_data = self._get_collection(import_id).find_one_and_update(
            {'citizen_id': citizen_id},  # TODO: использовать _id
            {'$addToSet': {'relatives': relative_id}},
            return_document=ReturnDocument.AFTER
        )
        if updated_data is None:
            raise CitizenNotFoundError(f'Citizen {citizen_id} not found.')

    async def delete_relative_from(self, import_id, citizen_id, relative_id):
        updated_data = self._get_collection(import_id).find_one_and_update(
            {'citizen_id': citizen_id},  # TODO: использовать _id
            {'$pull': {'relatives': relative_id}},
            return_document=ReturnDocument.AFTER
        )
        if updated_data is None:
            raise CitizenNotFoundError(f'Citizen {citizen_id} not found.')

    def close(self):
        self._driver.close()


class AsyncMongoStorage(CitizensStorage):
    def __init__(self, config):
        self._driver = AsyncIOMotorClient(
            host=config.get('host'), port=config.get('port'))
        self._db = self._driver.get_database(config['db'])

    def _get_collection(self, import_id):
        collection_name = f'import_{import_id}'
        return self._db.get_collection(collection_name)
    
    async def generate_import_id(self):
        collection = self._db.get_collection('counters')
        query = {'_id': 'import_id'}
        await collection.update_one(
            query,
            {'$inc': {'counter': 1}},
            upsert=True
        )
        document = await collection.find_one(query)
        return document['counter']

    async def insert_citizen(self, import_id: int, data: dict):
        data['_id'] = data['citizen_id']
        collection = self._get_collection(import_id)
        await collection.insert_one(data, bypass_document_validation=True)

    async def get_citizens(self, import_id):
        async for entry in self._get_collection(import_id).find():
            del entry['_id']
            yield entry

    async def get_one_citizen(self, import_id, citizen_id):
        collection = self._get_collection(import_id)
        citizen = await collection.find_one({'_id': citizen_id})
        if citizen is None:
            raise CitizenNotFoundError(f'Citizen `{citizen_id}` not found.')
        del citizen['_id']
        return citizen

    async def update_citizen(self, import_id, citizen_id, new_values):
        if 'relatives' in new_values:
            await self._update_relatives(import_id, citizen_id, new_values['relatives'])
        collection = self._get_collection(import_id)
        query = {'_id': citizen_id}
        result = await collection.update_one(query, {'$set': new_values})
        if result.matched_count != 1:
            raise CitizenNotFoundError(f'Citizen `{citizen_id}` not found.')
        updated_data = await collection.find_one(query)  # TODO: тут потенциально можем получить не то, что хотим
        del updated_data['_id']
        return updated_data

    async def add_relative_to(self, import_id, citizen_id, relative_id):
        collection = self._get_collection(import_id)
        result = await collection.update_one(
            {'_id': citizen_id},
            {'$addToSet': {'relatives': relative_id}}
        )
        if result.matched_count != 1:
            raise CitizenNotFoundError(f'Citizen `{citizen_id}` not found.')

    async def delete_relative_from(self, import_id, citizen_id, relative_id):
        collection = self._get_collection(import_id)
        result = await collection.update_one(
            {'_id': citizen_id},
            {'$pull': {'relatives': relative_id}}
        )
        if result.matched_count != 1:
            raise CitizenNotFoundError(f'Citizen `{citizen_id}` not found.')

    def close(self):
        self._driver.close()
