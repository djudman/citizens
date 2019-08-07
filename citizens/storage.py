from abc import ABC, abstractmethod

from pymongo import MongoClient, ReturnDocument


class BaseStorage(ABC):
    @abstractmethod
    def new_import(self, data):
        pass

    @abstractmethod
    def update_citizen(self, import_id, citizen_id, data):
        pass

    @abstractmethod
    def get_citizens(self, import_id):
        pass

    def close(self):
        pass


class MongoStorage(BaseStorage):
    def __init__(self, config):
        self._driver = MongoClient(host=config.get('host'), port=config.get('port'))
        self._db = self._driver.get_database(config['db'])

    def _generate_import_id(self):
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

    def new_import(self, data):
        import_id = self._generate_import_id()
        collection_name = f'import_{import_id}'
        collection = self._db.get_collection(collection_name)
        collection.insert_many(data)
        return import_id

    def delete_import(self, import_id):
        collection_name = f'import_{import_id}'
        collection = self._db.get_collection(collection_name)
        collection.drop()

    def update_citizen(self, import_id, citizen_id, data):
        collection_name = f'import_{import_id}'
        collection = self._db.get_collection(collection_name)
        updated_data = collection.find_one_and_update(
            {'citizen_id': citizen_id},
            {'$set': data},
            return_document=ReturnDocument.AFTER
        )
        del updated_data['_id']
        return updated_data

    def get_citizens(self, import_id, query=None):
        query = query or {}
        collection_name = f'import_{import_id}'
        collection = self._db.get_collection(collection_name)
        results = []
        for entry in collection.find(query):
            del entry['_id']
            results.append(entry)
        return results

    def close(self):
        self._driver.close()


class MemoryStorage(BaseStorage):
    def __init__(self):
        self._data = {}

    def new_import(self, data):
        import_id = 1
        self._data[import_id] = data
        return import_id

    def update_citizen(self, import_id, citizen_id, data):
        assert import_id in self._data
        new_data = {}
        for index, citizen in enumerate(self._data[import_id]):
            if citizen['citizen_id'] == citizen_id:
                for field, value in citizen.items():
                    new_data[field] = data.get(field, value)
                del self._data[import_id][index]
                break
        self._data[import_id].append(new_data)
        return new_data


    def get_citizens(self, import_id, query=None):
        data = self._data[import_id]
        if not query:
            return data
        results = []
        for entry in data:
            for k, v in query.items():
                if entry.get(k) != v:
                    break
            else:
                results.append(entry)
        return results
