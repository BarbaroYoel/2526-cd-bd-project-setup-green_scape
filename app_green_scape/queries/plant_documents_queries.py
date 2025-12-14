from utils.mongo_connector import MongoConnector
from utils.database_connector import DatabaseConnector 

def get_plant_documentation(id_prod):
    coleccion = MongoConnector.get_collection()
    if coleccion is None:
        return None
        
    documento = coleccion.find_one(
        {"IDProd": id_prod},
        {"_id": 0, "IDProd": 0} 
    )
    return documento

def get_available_plants():
    query = "SELECT IDProd, NombreComun FROM Planta ORDER BY IDProd;"
    
    try:
        return DatabaseConnector.execute_query(query)
    except Exception as e:
        print(f"ERROR al consultar plantas en MySQL: {e}")
        return []