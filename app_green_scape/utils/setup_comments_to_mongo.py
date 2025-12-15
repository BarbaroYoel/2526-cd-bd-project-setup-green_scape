import sys
from datetime import datetime
from utils.database_connector import DatabaseConnector
from utils.mongo_connector import MongoConnector 

def migrate_comments():
    print("--- Iniciando Migración: SQL (Relacional) -> MongoDB (Documental) ---")
    
    try:
        query = "SELECT IDCom, Contenido, IDU, IDPub, IDPadre, Fecha FROM Comentar"
        sql_comments = DatabaseConnector.execute_query(query)
        print(f"Leídos {len(sql_comments)} comentarios de MySQL.")
    except Exception as e:
        print(f"Error leyendo SQL. Asegúrate que 'Comentar' exista y tenga datos. Error: {e}")
        sys.exit(1)

    collection = MongoConnector.get_collection(MongoConnector.COLLECTION_COMENTARIOS)
    
    if collection is None: 
        print("ERROR: No se pudo obtener la colección de MongoDB.")
        sys.exit(1)
        
    deleted = collection.delete_many({}) 
    print(f"Limpieza: Se eliminaron {deleted.deleted_count} documentos de la colección '{collection.name}'.")

    comment_map = {c['IDCom']: c for c in sql_comments}
    mongo_docs = []
    
    for row in sql_comments:
        current = row
        root_id = current['IDCom']
        depth = 0
        
        temp_parent_id = current['IDPadre']
        while temp_parent_id is not None:
            depth += 1
            if temp_parent_id in comment_map:
                parent = comment_map[temp_parent_id]
                root_id = parent['IDCom']
                temp_parent_id = parent['IDPadre']
            else:
                break 

        fecha_obj = row['Fecha']
        if not isinstance(fecha_obj, datetime):
            fecha_obj = datetime.combine(fecha_obj, datetime.min.time())
        
        doc = {
            "_id": row['IDCom'],          
            "Contenido": row['Contenido'],
            "IDU": row['IDU'],
            "IDPub": row['IDPub'],
            "IDPadre": row['IDPadre'],
            "IDRaiz": root_id,           
            "Nivel": depth,               
            "Fecha": fecha_obj
        }
        mongo_docs.append(doc)

    if mongo_docs:
        try:
            collection.insert_many(mongo_docs, ordered=False)
            print(f"Insertados {len(mongo_docs)} documentos en MongoDB.")
        except Exception as e:
            print(f"Advertencia/Error durante insert_many: {e}")
            
    else:
        print("No hay datos para migrar.")

if __name__ == "__main__":
    migrate_comments()