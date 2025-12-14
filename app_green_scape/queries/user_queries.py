from utils.database_connector import DatabaseConnector

def get_users():
    query = "SELECT IDU, Nombre FROM Usuario ORDER BY Nombre"
    
    return DatabaseConnector.execute_query(query)

def analisis_usuario(idu, fecha_inicial, fecha_final):
    query = "CALL sp_analisis_usuario(%s, %s, %s)"
    params = (idu, fecha_inicial, fecha_final)
    
    return DatabaseConnector.execute_query(query, params)
