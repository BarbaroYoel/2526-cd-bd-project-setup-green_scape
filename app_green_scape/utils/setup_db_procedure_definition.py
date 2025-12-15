from utils.database_connector import DatabaseConnector

SQL_PROCEDURE_DEFINITION = """
CREATE PROCEDURE sp_analisis_usuario(
    IN p_idu INT,
    IN p_fecha_inicial DATE,
    IN p_fecha_final DATE
)
BEGIN
    
    DECLARE total_publicaciones INT;
    DECLARE total_comentarios INT;
    DECLARE reacciones_dadas INT;
    DECLARE reacciones_recibidas INT;
    DECLARE total_compras INT;
    DECLARE monto_gastado FLOAT;
    DECLARE total_contribuciones INT;
    DECLARE planta_mas_comprada VARCHAR(40);
    DECLARE planta_mas_contribuida VARCHAR(40);

    SELECT COUNT(IDPub) INTO total_publicaciones
    FROM Publicacion
    WHERE IDU = p_idu;

    SELECT COUNT(IDPub) INTO total_comentarios
    FROM Comentar
    WHERE IDU = p_idu;
    
    SELECT COUNT(IDPub) INTO reacciones_dadas
    FROM Reaccionar
    WHERE IDU = p_idu
      AND Fecha BETWEEN p_fecha_inicial AND p_fecha_final;

    SELECT COUNT(R.IDPub) INTO reacciones_recibidas
    FROM Reaccionar R
    INNER JOIN Publicacion P ON R.IDPub = P.IDPub
    WHERE P.IDU = p_idu
      AND R.Fecha BETWEEN p_fecha_inicial AND p_fecha_final;

    SELECT
        COUNT(IDProd),
        COALESCE(SUM(Precio * Cantidad), 0)
    INTO
        total_compras,
        monto_gastado
    FROM Compra
    WHERE IDUC = p_idu
      AND Fecha BETWEEN p_fecha_inicial AND p_fecha_final;

    SELECT COUNT(IDProd) INTO total_contribuciones
    FROM Contribucion
    WHERE IDU = p_idu
      AND Fecha BETWEEN p_fecha_inicial AND p_fecha_final;

    SELECT P.Nombre INTO planta_mas_comprada
    FROM Compra C
    INNER JOIN Producto P ON C.IDProd = P.IDProd
    WHERE C.IDUC = p_idu
      AND C.Fecha BETWEEN p_fecha_inicial AND p_fecha_final
    GROUP BY P.Nombre
    ORDER BY SUM(C.Cantidad) DESC
    LIMIT 1;
    SET planta_mas_comprada = COALESCE(planta_mas_comprada, 'N/A');

    SELECT P.Nombre INTO planta_mas_contribuida
    FROM Contribucion C
    INNER JOIN Producto P ON C.IDProd = P.IDProd
    WHERE C.IDU = p_idu
      AND C.Fecha BETWEEN p_fecha_inicial AND p_fecha_final
    GROUP BY P.Nombre
    ORDER BY COUNT(C.IDProd) DESC
    LIMIT 1;
    SET planta_mas_contribuida = COALESCE(planta_mas_contribuida, 'N/A');

    SELECT
        total_publicaciones AS total_publicaciones,
        total_comentarios AS total_comentarios,
        reacciones_dadas AS reacciones_dadas,
        reacciones_recibidas AS reacciones_recibidas,
        total_compras AS total_compras,
        monto_gastado AS monto_gastado,
        total_contribuciones AS total_contribuciones,
        planta_mas_comprada AS planta_mas_comprada,
        planta_mas_contribuida AS planta_mas_contribuida;

    END
"""

def setup_stored_procedure():
    drop_sql = "DROP PROCEDURE IF EXISTS sp_analisis_usuario"

    print("Intentando eliminar el procedimiento almacenado existente...")
    try:
        DatabaseConnector.execute_query(drop_sql)
        print("Procedimiento almacenado eliminado (si existía).")
    except Exception as e:
        print(f"Advertencia al eliminar el procedimiento: {e}")

    print("Creando el procedimiento almacenado 'sp_analisis_usuario'...")
    try:
        DatabaseConnector.execute_query(SQL_PROCEDURE_DEFINITION)
        print("✅ Procedimiento almacenado 'sp_analisis_usuario' creado con éxito.")
        return True
    except Exception as e:
        print(f"❌ Error al crear el procedimiento almacenado: {e}")
        return False

if __name__ == '__main__':
    setup_stored_procedure()