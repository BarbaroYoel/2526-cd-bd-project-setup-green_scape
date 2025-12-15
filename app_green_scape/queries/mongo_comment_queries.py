from datetime import datetime
from utils.mongo_connector import MongoConnector

def sort_thread_topologically(comments, root_id):
    map_comments = {c['_id']: c for c in comments}
    tree = {c['_id']: [] for c in comments}
    
    for c in comments:
        padre = c.get('IDPadre')
        if padre and padre in tree:
            tree[padre].append(c['_id'])
            
    result = []
    def dfs(current_id):
        if current_id in map_comments:
            result.append(map_comments[current_id])
            children_ids = sorted(tree.get(current_id, []), key=lambda id: map_comments[id]['Fecha'])
            for child_id in children_ids:
                dfs(child_id)
    
    dfs(root_id)
    return result


def get_full_thread_mongo(root_id):
    collection = MongoConnector.get_collection(MongoConnector.COLLECTION_COMENTARIOS)
    
    if collection is None: return [] 
    
    cursor = collection.find({"IDRaiz": root_id}).sort("Fecha", 1)
    
    hilo = list(cursor)
    for doc in hilo:
        doc['IDCom'] = doc['_id']
        
    return sort_thread_topologically(hilo, root_id)


def insert_new_comment_mongo(contenido, idu, idpub, idpadre=None):
    collection = MongoConnector.get_collection(MongoConnector.COLLECTION_COMENTARIOS)
    if collection is None: return None
    
    id_raiz = None
    if idpadre is not None:
        padre = collection.find_one({"_id": idpadre}, {"IDRaiz": 1, "Nivel": 1})
        if padre:
            id_raiz = padre.get("IDRaiz")
            nivel_padre = padre.get("Nivel", 0)
            nivel_nuevo = nivel_padre + 1
        else:
            id_raiz = None
    
    if id_raiz is None:
        nivel_nuevo = 0
        
    doc = {
        "Contenido": contenido,
        "IDU": idu,
        "IDPub": idpub,
        "IDPadre": idpadre,
        "Fecha": datetime.now(),
        "Nivel": nivel_nuevo, 
        "IDRaiz": None 
    }
    
    try:
        resultado = collection.insert_one(doc)
        new_id = resultado.inserted_id
        
       
        if id_raiz is None:
            collection.update_one(
                {"_id": new_id},
                {"$set": {"IDRaiz": new_id}}
            )
            id_raiz = new_id

        return new_id
    except Exception as e:
        print(f"Error al insertar comentario en MongoDB: {e}")
        return None

def delete_comment_mongo(comment_id):
    collection = MongoConnector.get_collection(MongoConnector.COLLECTION_COMENTARIOS)
    if collection is None: return 0
    
    try:
        resultado = collection.delete_one({"_id": comment_id})
        return resultado.deleted_count
    except Exception as e:
        print(f"Error al eliminar comentario Mongo ID {comment_id}: {e}")
        return 0
