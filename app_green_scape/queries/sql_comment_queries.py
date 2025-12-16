from utils.database_connector import DatabaseConnector

def get_full_thread_sql(root_comment_id):
    query = """
    WITH RECURSIVE HiloConversacion AS (
        SELECT 
            IDCom, 
            Contenido, 
            IDU, 
            IDPadre, 
            Fecha,
            0 AS Nivel
        FROM 
            Comentar
        WHERE 
            IDCom = %s

        UNION ALL

        SELECT 
            c.IDCom, 
            c.Contenido,  
            c.IDU, 
            c.IDPadre, 
            c.Fecha,
            hc.Nivel + 1
        FROM 
            Comentar c
        INNER JOIN 
            HiloConversacion hc ON c.IDPadre = hc.IDCom
    )
    SELECT 
        IDCom, Contenido, IDU, IDPadre, Nivel 
    FROM 
        HiloConversacion 
    ORDER BY 
        Nivel ASC, Fecha ASC;
    """
    
    try:
        resultados = DatabaseConnector.execute_query(query, (root_comment_id,))
        return resultados
    except Exception as e:
        raise Exception(f"Error recuperando hilo SQL: {e}")


def get_available_users():
    query = "SELECT IDU, Nombre FROM Usuario "
    try:
        results = DatabaseConnector.execute_query(query)
        return {r['IDU']: f"{r['Nombre']} (ID {r['IDU']})" for r in results}
    except Exception as e:
        print(f"Advertencia: No se pudieron cargar usuarios. Error: {e}")
        return {1: "Usuario 1 (Demo)", 2: "Usuario 2 (Demo)", 3: "Usuario 3 (Demo)"}

def get_available_publications():
    query = "SELECT IDPub, Texto FROM Publicacion " 
    try:
        results = DatabaseConnector.execute_query(query)
        return {r['IDPub']: f"{r.get('Texto', 'Publicación sin texto')} (ID: {r['IDPub']})" for r in results}
    except Exception as e:
        print(f"❌ ERROR: No se pudieron cargar publicaciones. Verifique la tabla Publicacion. Error: {e}")
        return {} 

def get_root_comments_for_pub(id_pub):
    query = """
    SELECT 
        IDCom, 
        LEFT(Contenido, 70) AS Snippet, 
        IDU,
        Fecha
    FROM 
        Comentar
    WHERE 
        IDPub = %s AND IDPadre IS NULL
    ORDER BY 
        Fecha DESC;
    """
    try:
        return DatabaseConnector.execute_query(query, (id_pub,))
    except Exception as e:
        print(f"Error al cargar hilos raíz: {e}")
        return []

def insert_new_comment_sql(contenido, idu, idpub, idpadre=None):
    sql = "INSERT INTO Comentar (Contenido, IDU, IDPub, IDPadre) VALUES (%s, %s, %s, %s)"
    conn = DatabaseConnector.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (contenido, idu, idpub, idpadre))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error al insertar comentario: {e}")
        conn.rollback()
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_comment_sql(comment_id):
    sql = "DELETE FROM Comentar WHERE IDCom = %s"
    
    conn = DatabaseConnector.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (comment_id,))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Error al eliminar comentario SQL ID {comment_id}: {e}")
        conn.rollback()
        return 0
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_available_publications():
    """Obtiene una lista de publicaciones para el selector desde SQL."""
    query = "SELECT IDPub, Texto FROM Publicacion LIMIT 50" 
    try:
        results = DatabaseConnector.execute_query(query)
        return {r['IDPub']: f"{r.get('Texto', 'Publicación sin texto')} (ID: {r['IDPub']})" for r in results}
    except Exception as e:
        print(f"Error en get_available_publications: {e}")
        return {}