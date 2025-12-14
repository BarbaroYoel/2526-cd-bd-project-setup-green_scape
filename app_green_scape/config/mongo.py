import os
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')
MONGO_DB_NAME = os.getenv('MONGO_DATABASE', 'GreenScapeDocs')

if MONGO_USER and MONGO_PASSWORD:
    MONGO_URI_AUTH = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
else:
    MONGO_URI_AUTH = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"


MONGO_CONFIG = {
    'uri': os.getenv('MONGO_URI', MONGO_URI_AUTH), 
    'database': MONGO_DB_NAME,
    'collection_name': 'PlantasDocumentacion'
}