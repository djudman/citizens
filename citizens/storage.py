import asyncio
import datetime
import functools
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

import pymongo


class CitizensStorageError(Exception):
    pass


class ImportNotFound(CitizensStorageError):
    pass


class CitizenNotFound(CitizensStorageError):
    pass


class RelativeNotFound(CitizensStorageError):
    pass


class BaseCitizensStorage(metaclass=ABCMeta):
    def __init__(self, config: dict):
        pass

    @abstractmethod
    async def import_citizens(self, citizens: List[Dict]):
        pass

    @abstractmethod
    async def get_citizens(self, import_id: int, query: dict=None,
                           return_fields: List[str]=None):
        pass

    @abstractmethod
    async def update_citizen(self, import_id: int, citizen_id: int, values: dict):
        pass

    @abstractmethod
    async def get_presents_by_month(self, import_id: int):
        pass

    @abstractmethod
    async def get_ages_by_town(self, import_id: int):
        pass

    @abstractmethod
    async def close(self):
        pass


class AsyncMongoStorage(BaseCitizensStorage):
    def __init__(self, config):
        self._driver = pymongo.MongoClient(config['connection_string'])
        self._db = self._driver.get_database(config['db'])
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()
        self._async_run = functools.partial(loop.run_in_executor, executor)
        self._collections_cache = {}

    async def _async(self, callable, *args, **kwargs):
        func = functools.partial(callable, *args, **kwargs)
        return await self._async_run(func)

    def _get_collection(self, import_id, create_if_not_exists=False):
        name = f'citizens_import_{import_id}'
        if name in self._collections_cache:
            return self._collections_cache[name]
        db = self._db
        found = list(db.list_collection_names(filter={'name': name}))
        if not found and not create_if_not_exists:
            raise ImportNotFound(f'Import `{import_id}` does not exists.')
        obj = db.get_collection(name)
        self._collections_cache[name] = obj
        return obj
    
    async def _generate_import_id(self):
        collection = self._db.get_collection('counters')
        document = await self._async(
            collection.find_one_and_update,
            {'_id': 'import_id'},
            {'$inc': {'counter': 1}},
            return_document=pymongo.ReturnDocument.AFTER,
            upsert=True
        )
        return document['counter']

    async def import_citizens(self, citizens: List[Dict]):
        import_id = await self._generate_import_id()
        collection = self._get_collection(import_id, create_if_not_exists=True)
        collection.create_index([('citizen_id', pymongo.ASCENDING)], background=True)
        await self._async(collection.insert_many, citizens)
        return import_id

    async def get_citizens(self, import_id: int, filter: dict=None,
                           return_fields: List[str]=None):
        collection = self._get_collection(import_id)
        query = {}
        if filter is not None:
            for name, value in filter.items():
                if isinstance(value, list):
                    query[name] = {'$in': value}
                else:
                    query[name] = value
        projection = {'_id': False}
        if return_fields is not None:
            projection = return_fields
        return await self._async(
            collection.find,
            filter=query,
            projection=projection
        )

    async def update_citizen(self, import_id: int, citizen_id: int, values: dict):
        collection = self._get_collection(import_id)
        old_data = await self._async(
            collection.find_one_and_update,
            {'citizen_id': citizen_id},
            {'$set': values},
            projection={'_id': False},
            return_document=pymongo.ReturnDocument.BEFORE
        )
        if not old_data:
            raise CitizenNotFound(f'Citizen `{citizen_id}` not found.')
        new_relatives = values.get('relatives')
        if new_relatives is not None:
            old_relatives = old_data['relatives']
            # NOTE: Удаляем на той стороне меня из relatives
            for rid in old_relatives:
                if rid not in new_relatives:
                    try:
                        await self._delete_relative(import_id, rid, citizen_id)
                    except CitizenNotFound as e:
                        # TODO: откатить обновленные данные. 
                        # Но вот только их кто-нибудь может успеть обновить ещё раз
                        raise RelativeNotFound(f'Relative `{rid}` not found.') from e
            # NOTE: Добавляем на той стороне меня в relatives
            for rid in new_relatives:
                if rid not in old_relatives:
                    try:
                        await self._add_relative(import_id, rid, citizen_id)
                    except CitizenNotFound as e:
                        # TODO: откатить обновленные данные. 
                        # Но вот только их кто-нибудь может успеть обновить ещё раз
                        raise RelativeNotFound(f'Relative `{rid}` not found.') from e
        old_data.update(values)
        return old_data

    async def _add_relative(self, import_id, citizen_id, relative_id):
        collection = self._get_collection(import_id)
        updated = await self._async(
            collection.find_one_and_update,
            {'citizen_id': citizen_id},
            {'$addToSet': {'relatives': relative_id}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if not updated:
            raise CitizenNotFound(f'Citizen `{citizen_id}` not found.')

    async def _delete_relative(self, import_id, citizen_id, relative_id):
        collection = self._get_collection(import_id)
        updated = await self._async(
            collection.find_one_and_update,
            {'citizen_id': citizen_id},
            {'$pull': {'relatives': relative_id}},
            return_document=pymongo.ReturnDocument.AFTER
        )
        if not updated:
            raise CitizenNotFound(f'Citizen `{citizen_id}` not found.')

    async def get_presents_by_month(self, import_id: int):
        collection = self._get_collection(import_id)
        return await self._async(collection.aggregate, [
            {'$project': {'_id': 0, 'citizen_id': 1, 'relatives': 1, 'birth_date': {'$dateFromString': {'dateString': "$birth_date", 'format': "%d.%m.%Y"}}, 'num_relatives': {'$size': "$relatives"}}},
            {'$match': { 'num_relatives': {'$gt': 0}}},
            {'$unwind': "$relatives"},
            {'$project': {'citizen_id': "$relatives", 'relative_birth_month': {'$month': "$birth_date"}, 'relative_id': "$citizen_id"}},
            {'$group': {'_id': {'month': "$relative_birth_month", 'citizen_id': "$citizen_id"}, 'presents': {'$sum' : 1}}},
            {'$group': {'_id': "$_id.month", 'citizens': {'$push': {'citizen_id': "$_id.citizen_id", 'presents': {'$sum': "$presents"}}}}},
            {'$project': {'_id': 0, 'month': "$_id", 'citizens': 1}}
        ])

    async def get_ages_by_town(self, import_id: int):
        collection = self._get_collection(import_id)
        return await self._async(collection.aggregate, [
            {
                '$project': {
                    '_id': 0,
                    'town': 1,
                    'citizen_id': 1,
                    'age': {
                        '$subtract': [
                            { # current year
                                '$year': datetime.datetime.now(),
                            },
                            { # birth year
                                '$year': {'$dateFromString': {'dateString': "$birth_date", 'format': "%d.%m.%Y"}}
                            }
                        ]
                    }
                }
            },
            {'$group': { '_id': '$town', 'ages': {'$push': '$age'}}},
            {'$project': {'_id': 0, 'town': "$_id", 'ages': 1}},
            {'$sort': {'town': 1}}
        ])

    async def close(self):
        await self._async(self._driver.close)
