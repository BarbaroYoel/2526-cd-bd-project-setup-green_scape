import mysql.connector
from config.database import DB_CONFIG

class DatabaseConnector:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(**DB_CONFIG)

    @staticmethod
    def execute_query(query, params=None):
        conn = DatabaseConnector.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or [])
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        finally:
            cursor.close()
            conn.close()