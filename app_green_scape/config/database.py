import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'greenscape_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'greenscape_pass'),
    'database': os.getenv('MYSQL_DATABASE', 'GreenScape'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}