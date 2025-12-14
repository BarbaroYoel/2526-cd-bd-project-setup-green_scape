from utils.database_connector import DatabaseConnector

def get_all_products():
    """3.a: Listar todos los productos disponibles"""
    query = """
    SELECT IDProd, Nombre, Descripcion, Precio
    FROM Producto
    ORDER BY Nombre;
    """
    return DatabaseConnector.execute_query(query)

def get_monthly_activity_average():
    """3.g: Promedio de actividad mensual"""
    query = """
    WITH ActivityPerMonth AS (
    SELECT
        u.IDU,
        u.Nombre,
        YEAR(c.Fecha) AS Anio,
        MONTH(c.Fecha) AS Mes,
          (COUNT(DISTINCT cf.IDF) + COUNT(DISTINCT cv.IDV)) AS Total_Multimedia
    FROM Usuario u
    JOIN Contribucion c ON u.IDU = c.IDU
    LEFT JOIN Contribucion_Foto cf ON c.IDProd = cf.IDProd AND c.Fecha = cf.Fecha
    LEFT JOIN Contribucion_Video cv ON c.IDProd = cv.IDProd AND c.Fecha = cv.Fecha
    WHERE c.Fecha >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
    GROUP BY u.IDU, u.Nombre, YEAR(c.Fecha), MONTH(c.Fecha)
)
SELECT
    IDU,
    Nombre,
    AVG(Total_Multimedia) AS Promedio_Mensual_Multimedia
FROM ActivityPerMonth
GROUP BY IDU, Nombre
ORDER BY Promedio_Mensual_Multimedia DESC
LIMIT 10;
    """
    return DatabaseConnector.execute_query(query)

def get_category_preference_changes():
    query="""
WITH ContribucionesPorAnio AS (
    SELECT 
        u.IDU,
        u.Nombre,
        YEAR(c.Fecha) AS Anio,
        p.Categoria,
        COUNT(*) AS Total_Por_Categoria
    FROM Usuario u
    JOIN Contribucion c ON u.IDU = c.IDU
    JOIN Planta p ON c.IDProd = p.IDProd
    GROUP BY u.IDU, u.Nombre, YEAR(c.Fecha), p.Categoria
),
CategoriaFavorita AS (
    SELECT 
        IDU,
        Nombre,
        Anio,
        Categoria,
        ROW_NUMBER() OVER(PARTITION BY IDU, Anio ORDER BY Total_Por_Categoria DESC) as Ranking
    FROM ContribucionesPorAnio
)
SELECT 
    T1.IDU,
    T1.Nombre,
    T1.Anio AS Anio_Anterior,
    T1.Categoria AS Categoria_Anterior,
    T2.Anio AS Anio_Actual,
    T2.Categoria AS Categoria_Nueva
FROM CategoriaFavorita T1
JOIN CategoriaFavorita T2 
    ON T1.IDU = T2.IDU 
    AND T1.Anio = T2.Anio - 1 
WHERE T1.Ranking = 1 
  AND T2.Ranking = 1
  AND T1.Categoria <> T2.Categoria;
    """
    return DatabaseConnector.execute_query(query)
