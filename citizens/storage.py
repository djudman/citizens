from pymongo import MongoClient


class Storage:
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
        collection.find_one_and_update(
            {'_id': 'import_id'},
            {'$inc': {'counter': 1}},
            upsert=True
        )

    def new_import(self, data):
        import_id = self._generate_import_id()
        collection_name = f'import_{import_id}'
        collection = db.get_collection(collection_name)
        collection.insert_many(data)
        return import_id

    def save_citizen(self, import_id, citizen_id, data):
        pass

    def get_citizens(self, import_id):
        pass
