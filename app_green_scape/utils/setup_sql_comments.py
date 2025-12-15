import sys
from utils.database_connector import DatabaseConnector
import mysql.connector 

def setup_sql_comments_db():
    conn = DatabaseConnector.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        conn.commit()

        
        old_schema_exists = False
        try:
            cursor.fetchall() 
            old_schema_exists = True
        except mysql.connector.Error as e:
            if e.errno == 1054: 
                print("La tabla 'Comentar' ya existe con el esquema nuevo o no se pudo verificar el esquema antiguo.")
            else:
                 print(f"La tabla 'Comentar' no existe o tiene otro error: {e}")

        
        if old_schema_exists:
            print("Detectado esquema antiguo de 'Comentar'. Iniciando migración de datos...")
            
            cursor.execute("RENAME TABLE Comentar TO Comentar_old;")
            conn.commit()
            print("Tabla 'Comentar' renombrada a 'Comentar_old'.")
            
            create_table_query = """
            CREATE TABLE Comentar (
                IDCom INT AUTO_INCREMENT PRIMARY KEY,
                Contenido VARCHAR(400) NOT NULL,
                Fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                IDU INT NOT NULL,
                IDPub INT NOT NULL,
                IDPadre INT NULL,
                
                FOREIGN KEY (IDU) REFERENCES Usuario(IDU) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (IDPub) REFERENCES Publicacion(IDPub) ON DELETE RESTRICT ON UPDATE CASCADE, 
                FOREIGN KEY (IDPadre) REFERENCES Comentar(IDCom) ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_query)
            conn.commit()
            print("Nueva tabla 'Comentar' creada con esquema de hilos (IDCom, IDPadre).")

            transfer_query = """
            INSERT INTO Comentar (IDU, IDPub, Contenido, Fecha) 
            SELECT 
                IDU, 
                IDPub, 
                Comentario, 
                NOW() -- Asignamos la fecha actual ya que el esquema antiguo no tenía timestamp
            FROM 
                Comentar_old;
            """
            cursor.execute(transfer_query)
            conn.commit()
            migrated_count = cursor.rowcount
            print(f"Transferidos {migrated_count} comentarios existentes de init.sql. Estos se consideran ahora comentarios 'Raíz'.")
            
            cursor.execute("SELECT MAX(IDCom) FROM Comentar;")
            max_id_result = cursor.fetchone()
            max_id = max_id_result[0] if max_id_result and max_id_result[0] is not None else 0
            
            next_id = max_id + 1
            cursor.execute(f"ALTER TABLE Comentar AUTO_INCREMENT = {next_id};")
            conn.commit()
            print(f"AUTO_INCREMENT ajustado a {next_id} para nuevas inserciones.")
            
            cursor.execute("DROP TABLE Comentar_old;")
            conn.commit()
            
        else:
            print("Recreando tabla 'Comentar' limpia para soportar hilos...")
            cursor.execute("DROP TABLE IF EXISTS Comentar;")
            create_table_query = """
            CREATE TABLE Comentar (
                IDCom INT AUTO_INCREMENT PRIMARY KEY,
                Contenido VARCHAR(400) NOT NULL,
                Fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                IDU INT NOT NULL,
                IDPub INT NOT NULL,
                IDPadre INT NULL,
                
                FOREIGN KEY (IDU) REFERENCES Usuario(IDU) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (IDPub) REFERENCES Publicacion(IDPub) ON DELETE RESTRICT ON UPDATE CASCADE, 
                FOREIGN KEY (IDPadre) REFERENCES Comentar(IDCom) ON DELETE CASCADE
            );
            """
            cursor.execute(create_table_query)
            conn.commit()
            print("Tabla 'Comentar' recreada con éxito.")


        
        id_pub_test = 1 
        usuarios_ids = [1, 2, 3] 
        
        sql_insert = "INSERT INTO Comentar (Contenido, IDU, IDPub, IDPadre) VALUES (%s, %s, %s, %s)"
        root_msg = "Hilo de Prueba: ¿Cuál es el mejor abono para el Filodendro?"
        cursor.execute(sql_insert, (root_msg, usuarios_ids[0], id_pub_test, None))
        conn.commit()
        
        root_id = cursor.lastrowid
        if not root_id:
             raise Exception("No se pudo obtener el ID del comentario raíz.")

        print(f"Comentario Raíz del hilo de prueba creado (ID: {root_id})")

        current_padre_id = root_id
        
        mensajes_cadena = [
            "Yo recomiendo humus de lombriz.", "Es mejor que el fertilizante líquido semanal?", 
            "Sí, el humus mejora la estructura del suelo a largo plazo.", "Genial, ¿y qué tan a menudo lo aplicas?", 
            "Cada 3 meses es suficiente para un interior.", "¿Y si el suelo es arcilloso?", 
            "Ahí debes mezclarlo con perlita para mejorar el drenaje.", "Gracias, lo haré de inmediato.", 
            "No olvides limpiar el polvo de las hojas primero.", "Buena idea, eso bloquea la luz.", 
            "¿Algún truco para evitar la araña roja?", "Necesitas aumentar la humedad ambiental.", 
            "Difícil en mi casa que es muy seca.", "Prueba a rociar las hojas con agua destilada a diario.", 
            "¿Por qué no del grifo?", "El cloro y sales del grifo queman las puntas.", 
            "Tiene sentido. ¿Qué pasa con los trips?", "El Neem es lo más efectivo para tratamientos puntuales.", 
            "¿Dónde se compra el aceite de Neem?", "En cualquier vivero grande o en línea.", 
            "¿Debo diluirlo?", "Sí, 1ml por litro de agua con jabón neutro.", 
            "Perfecto, probaré la receta esta noche.", "¡Éxito con tu Filodendro!"
        ]

        for i, msj in enumerate(mensajes_cadena):
            usuario_actual = usuarios_ids[(i + 1) % len(usuarios_ids)]
            
            cursor.execute(sql_insert, (f"R{i+1}: {msj}", usuario_actual, id_pub_test, current_padre_id))
            conn.commit()
            
            current_padre_id = cursor.lastrowid
        
        print(f"Conversación de prueba generada con éxito. Total de niveles: {1 + len(mensajes_cadena)}")

    except Exception as e:
        print(f"Error fatal durante la configuración SQL: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
        except Exception as e:
            print(f"Advertencia: No se pudieron reactivar las comprobaciones de FK: {e}")
        
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    setup_sql_comments_db()