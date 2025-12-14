from pymongo import MongoClient
from config.mongo import MONGO_CONFIG


class MongoConnector:
    _client = None
    _collection = None
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                cls._client = MongoClient(MONGO_CONFIG['uri'])
                cls._client.admin.command('ping') 
                print("Conexión a MongoDB establecida.")
            except Exception as e:
                print(f"ERROR: No se pudo conectar a MongoDB en {MONGO_CONFIG['uri']}. Error: {e}")
                cls._client = None
        return cls._client

    @classmethod
    def get_collection(cls):
        if cls._collection is None and cls.get_client():
            db = cls._client[MONGO_CONFIG['database']]
            cls._collection = db[MONGO_CONFIG['collection_name']]
        return cls._collection