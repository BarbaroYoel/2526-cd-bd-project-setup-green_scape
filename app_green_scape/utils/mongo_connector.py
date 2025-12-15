from pymongo import MongoClient

from config.mongo import MONGO_CONFIG 

class MongoConnector:
    _client = None
    _database = None
    
    MONGO_URI = MONGO_CONFIG['uri']  
    DB_NAME = MONGO_CONFIG['database'] 
    
   
    COLLECTION_PLANTAS = "plantas"          
    COLLECTION_COMENTARIOS = "comentarios" 

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                auth_source = "admin" if "root" in cls.MONGO_URI else None
                
                cls._client = MongoClient(cls.MONGO_URI, 
                                          serverSelectionTimeoutMS=5000,
                                          authSource=auth_source
                                         )
                cls._client.admin.command('ping')
            except Exception as e:
                print(f"Error al conectar a MongoDB: {e}")
                return None
        return cls._client

    @classmethod
    def get_database(cls):
        client = cls.get_client()
        if client is not None:
            if cls._database is None:
                cls._database = client[cls.DB_NAME]
            return cls._database
        return None

    @classmethod
    def get_collection(cls, name):
        """
        Retorna una colección específica por su nombre.
        """
        db = cls.get_database()
        if db is not None:
            return db[name]
        return None