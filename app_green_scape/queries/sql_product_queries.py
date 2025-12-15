from utils.database_connector import DatabaseConnector

def fetch_products_with_price():
    """Consulta la lista de productos con su precio actual (Solo DB)."""
    query = """
    SELECT 
        IDProd,
        Nombre,
        Precio
    FROM Producto
    ORDER BY Nombre;
    """
    return DatabaseConnector.execute_query(query)

def update_product_price_db(product_id, new_price):
    """
    Actualiza el precio de un producto (Solo DB).
    """
    query = "UPDATE Producto SET Precio = %s WHERE IDProd = %s;"
    return DatabaseConnector.execute_ddl_dml(query, (new_price, product_id))

def fetch_price_history(product_id):
    query = f"""
    SELECT 
        HP.IDA, 
        HP.Precio_Anterior, 
        HP.Precio_Nuevo, 
        HP.Porcentaje_Cambio, 
        DATE_FORMAT(HP.Fecha_Cambio, '%Y-%m-%d %H:%i:%s') AS Fecha_Cambio_Fmt
    FROM Historial_Precios HP
    WHERE HP.IDProd = {product_id}
    ORDER BY HP.Fecha_Cambio DESC;
    """
    return DatabaseConnector.execute_query(query)