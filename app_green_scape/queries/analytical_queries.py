from utils.database_connector import DatabaseConnector

def get_all_products():
    """a: Listar todos los productos disponibles"""
    query = """
    SELECT IDProd, Nombre, Descripcion, Precio
    FROM Producto
    ORDER BY Nombre;
    """
    return DatabaseConnector.execute_query(query)

def query_b_top_reactions():
    """b: Publicaciones con mayor cantidad de Reacciones"""
    query = """
SELECT usu.Nombre ,pub.Texto, Count(*) as Cantidad_de_Reacciones
FROM Reaccionar rcc
JOIN Publicacion pub ON rcc.IDPub = pub.IDPub
JOIN Usuario usu ON pub.IDU = usu.IDU
GROUP BY rcc.IDPub, pub.Texto, usu.Nombre
ORDER BY Cantidad_de_Reacciones DESC;
"""
    return DatabaseConnector.execute_query(query)

def query_c_likes_by_product():
    """c: Conteo de 'Me Gusta' por producto"""
    query = """
SELECT gus.IDProd, COUNT(*) AS Likes
FROM Gustar gus
GROUP BY gus.IDProd
ORDER BY Likes DESC;
"""
    return DatabaseConnector.execute_query(query)

def query_d_last_activity_6m():
    """d: Fecha de última actividad de Usuario (Reacción o Contribución)"""
    query = """
SELECT usu.IDU, usu.Nombre, usu.DireccionParticular,
MAX(
    CASE
        WHEN rcc.Fecha >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) OR ctr.Fecha >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        THEN GREATEST(COALESCE(rcc.Fecha, '1223-01-01'), COALESCE(ctr.Fecha, '1223-01-01'))
        ELSE NULL
    END
) AS Fecha_Ultima_Actividad
FROM Usuario usu
LEFT JOIN Reaccionar rcc ON usu.IDU = rcc.IDU
LEFT JOIN Contribucion ctr ON usu.IDU = ctr.IDU
GROUP BY usu.IDU, usu.Nombre, usu.DireccionParticular
ORDER BY Fecha_Ultima_Actividad DESC;
"""
    return DatabaseConnector.execute_query(query)

def query_e_pos_vs_neg_reactions():
    """e: Publicaciones con más reacciones Positivas que Negativas"""
    query = """
SELECT pub.*, COUNT(rcc.IDU) AS Total_Reacciones
FROM Publicacion pub
JOIN Reaccionar rcc ON pub.IDPub = rcc.IDPub
GROUP BY pub.IDPub
HAVING COUNT(CASE
                WHEN rcc.Tipo IN ('Me encanta', 'Me gusta', 'Me asombra', 'Me divierte') THEN 1 END) >
        COUNT(CASE
                WHEN rcc.Tipo IN ('Me enoja', 'Me entristece') THEN 1 END)
ORDER BY Total_Reacciones DESC;
"""
    return DatabaseConnector.execute_query(query)

def query_f_consecutive_contributions():
    """f: Plantas con Contribuciones en Meses Consecutivos (por cualquier usuario)."""
    query = """
WITH MesesDeContribucion AS (
    SELECT DISTINCT
        ctr.IDProd,
        plt.NombreComun,
        YEAR(ctr.Fecha) AS Anio,
        MONTH(ctr.Fecha) AS Mes
    FROM Contribucion AS ctr
    JOIN Planta AS plt ON ctr.IDProd = plt.IDProd
),
MesesRankeados AS (
    SELECT
        NombreComun,
        (Anio * 12) + Mes AS Mes_Secuencial_Actual,
        LAG((Anio * 12) + Mes, 1) OVER (PARTITION BY IDProd ORDER BY Anio, Mes) AS Mes_Secuencial_Anterior
    FROM MesesDeContribucion
)
SELECT DISTINCT
    NombreComun
FROM MesesRankeados
WHERE 
    Mes_Secuencial_Actual = Mes_Secuencial_Anterior + 1
ORDER BY NombreComun;
"""
    return DatabaseConnector.execute_query(query)

# SELECT 
#     plt.NombreComun,
#     YEAR(ctr.Fecha) AS Anio,
#     MONTH(ctr.Fecha) AS Mes,
#     COUNT(*) AS Total_Contribuciones_En_Mes
# FROM Contribucion AS ctr
# JOIN Planta AS plt ON ctr.IDProd = plt.IDProd
# GROUP BY plt.NombreComun, Anio, Mes
# ORDER BY plt.NombreComun, Anio, Mes;



def get_monthly_activity_average():
    """g: Promedio de actividad mensual"""
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

def query_h_age_distribution():
    """h: Distribución de Usuarios por Rango de Edad"""
    query = """
SELECT
(CASE
    WHEN  YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) < 11 THEN "wtf"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 11 AND 20 THEN "11-20"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 21 AND 30 THEN "21-30"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 31 AND 40 THEN "31-40"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 41 AND 50 THEN "41-50"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 51 AND 60 THEN "51-60"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 61 AND 70 THEN "61-70"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 71 AND 80 THEN "71-80"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 81 AND 90 THEN "81-90"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) BETWEEN 91 AND 100 THEN "91-100"
    WHEN YEAR(CURDATE()) - YEAR(usu.FechaDeNacimiento) > 100 THEN "en mis tiempos..."
ELSE "Revisate Eso"
END) AS Rango_de_Edad,
COUNT(*) AS Cant_de_Usuarios,
(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Usuario)) AS Porcentaje
FROM Usuario usu
GROUP BY Rango_de_Edad
ORDER BY Rango_de_Edad;
"""
    return DatabaseConnector.execute_query(query)

def query_i_stable_purchase_patterns():
    """i: Productos que no han mostrado un incremento en sus ventas mes a mes durante el último año."""
    query = """
WITH VentasMensuales AS (
    SELECT
        c.IDProd,
        p.Nombre AS NombrePlanta,
        YEAR(c.Fecha) AS Anio,
        MONTH(c.Fecha) AS Mes,
        SUM(c.Cantidad) AS Total_Vendido
    FROM Compra c
    JOIN Producto p ON c.IDProd = p.IDProd
    WHERE c.Fecha BETWEEN DATE_SUB(CURDATE(), INTERVAL 48 MONTH) AND CURDATE()
    GROUP BY c.IDProd, p.Nombre, Anio, Mes
),
ComparacionMensual AS (
    SELECT
        IDProd,
        NombrePlanta,
        Anio,
        Mes,
        Total_Vendido,
        LAG(Total_Vendido, 1, 0) OVER (PARTITION BY IDProd ORDER BY Anio, Mes) AS Venta_Mes_Anterior
    FROM VentasMensuales
)
-- 3. Identificamos los productos que NO han tenido un incremento constante.
SELECT DISTINCT
    IDProd,
    NombrePlanta
FROM ComparacionMensual
-- Buscamos productos que en AL MENOS un mes, la venta actual NO FUE mayor que la anterior (<=).
-- Si al menos un mes no creció, el patrón no es de "incremento constante".
WHERE Total_Vendido <= Venta_Mes_Anterior 
ORDER BY IDProd;
"""
    return DatabaseConnector.execute_query(query)

def contribution_trends_by_climate():
    """j: Tendencias de Contribución por Clima"""
    query="""  
SELECT 
    ranking.Tipo as Tipo_Clima,
    IFNULL(contrib.Total_Contribuciones, 0) as Total_Contribuciones,
    IFNULL(contrib.Contribuciones_con_Fotos, 0) as Contribuciones_Fotos,
    IFNULL(contrib.Contribuciones_con_Videos, 0) as Contribuciones_Videos,
    IFNULL(contrib.Usuarios_Contribuyentes, 0) as Usuarios_Contribuyentes,
    ranking.NombreComun as Planta_Mas_Popular,
    ranking.Gustado as Me_Gusta
FROM (
    SELECT *
    FROM (
        SELECT 
            c.Tipo,
            p.NombreComun,
            COUNT(g.IDU) as Gustado,
            ROW_NUMBER() OVER (PARTITION BY c.Tipo ORDER BY COUNT(g.IDU) DESC) as rn
        FROM Gustar g
        JOIN Planta p ON g.IDProd = p.IDProd
        JOIN Clima c ON p.IDC = c.IDC
        GROUP BY c.Tipo, p.NombreComun
    ) sub1
    WHERE rn = 1
) ranking
JOIN (
    SELECT 
        c.Tipo,
        COUNT(*) as Total_Contribuciones,
        COUNT(DISTINCT cf.IDF) as Contribuciones_con_Fotos,
        COUNT(DISTINCT cv.IDV) as Contribuciones_con_Videos,
        COUNT(DISTINCT cont.IDU) as Usuarios_Contribuyentes
    FROM Contribucion cont
    JOIN Planta p ON cont.IDProd = p.IDProd
    JOIN Clima c ON p.IDC = c.IDC
    LEFT JOIN Contribucion_Foto cf ON cont.IDProd = cf.IDProd AND cont.Fecha = cf.Fecha
    LEFT JOIN Contribucion_Video cv ON cont.IDProd = cv.IDProd AND cont.Fecha = cv.Fecha
    GROUP BY c.Tipo
) contrib ON ranking.Tipo = contrib.Tipo
ORDER BY ranking.Tipo;  
"""
    return DatabaseConnector.execute_query(query)

def get_category_preference_changes():
    """k: Cambio de preferencias de categorías"""
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
    T1.Anio AS Anio_Inicial,
    T1.Categoria AS Categoria_Inicial,
    T2.Anio AS Anio_Final,
    T2.Categoria AS Categoria_Final
FROM CategoriaFavorita T1
JOIN CategoriaFavorita T2 ON T1.IDU = T2.IDU AND T1.Anio < T2.Anio
WHERE T1.Ranking = 1 AND T2.Ranking = 1 AND T1.Categoria <> T2.Categoria
ORDER BY T1.IDU, T1.Anio;
    """
    return DatabaseConnector.execute_query(query)


def top_rated_sellers():
    """n: Vendedores Mejor Valorados (Usando la tabla Compra)"""
    query="""
SELECT 
    u.Nombre, 
    u.DireccionParticular, 
    u.Email, 
    AVG(c.Puntuacion) AS Calificacion_Promedio, 
    SUM(c.Cantidad) AS total_productos_vendidos
FROM Compra AS c
JOIN Usuario AS u ON u.IDU = c.IDUV
WHERE c.Puntuacion IS NOT NULL
GROUP BY 
    u.Nombre, 
    u.DireccionParticular, 
    u.Email
ORDER BY 
    Calificacion_Promedio DESC
LIMIT 5;
"""
    return DatabaseConnector.execute_query(query)


def query_l_raritos_compra_vs_gusto():
    """l: Usuarios que Compran Productos que No les Gustan ('Raritos')"""
    query = """
SELECT 
    usu.IDU,
    usu.Nombre,
    SUM(CASE WHEN gus.IDProd IS NULL THEN 1 ELSE 0 END) AS Compras_No_Gustadas,
    SUM(CASE WHEN gus.IDProd IS NOT NULL THEN 1 ELSE 0 END) AS Compras_Gustadas
FROM Usuario usu
JOIN Compra com ON com.IDUC = usu.IDU  -- Compras realizadas por el usuario
LEFT JOIN Gustar gus ON gus.IDU = usu.IDU AND gus.IDProd = com.IDProd -- Gustos
GROUP BY usu.IDU, usu.Nombre
HAVING Compras_No_Gustadas > Compras_Gustadas
ORDER BY Compras_No_Gustadas DESC;
"""
    return DatabaseConnector.execute_query(query)

def query_m_users_without_multimedia():
    """m: Usuarios sin Publicaciones con Contenido Multimedia (Foto o Video)"""
    query = """
SELECT usu.IDU, usu.Nombre
FROM Usuario usu
WHERE usu.IDU NOT IN (
    SELECT DISTINCT pub.IDU
    FROM Publicacion pub
    LEFT JOIN Tener_Foto tf ON pub.IDPub = tf.IDPub
    WHERE tf.IDF IS NOT NULL OR pub.IDV IS NOT NULL
)
ORDER BY usu.IDU;
"""
    return DatabaseConnector.execute_query(query)

def analyze_influencers_impact():
    """
    p) Análisis de influencers: Top 5, sus plantas, impacto en ventas y conversión.
    """
    results = []

    sql_top_influencers = """
    WITH ReaccionesPonderadas AS (
        SELECT IDPub, 
               SUM(CASE 
                   WHEN Tipo = 'me gusta' THEN 1 
                   WHEN Tipo = 'me encanta' THEN 2 
                   WHEN Tipo = 'me asombra' THEN 1.5 
                   ELSE 0 END) as score_reac
        FROM Reaccionar GROUP BY IDPub
    ),
    ComentariosPonderados AS (
        SELECT IDPub, COUNT(*) * 2 as score_com
        FROM Comentar GROUP BY IDPub
    )
    SELECT 
        u.IDU, 
        u.Nombre,
        p.IDPub,
        (SELECT IDProd FROM Contribucion WHERE IDU = p.IDU ORDER BY Fecha DESC LIMIT 1) as IDProd,
        
        (SELECT Fecha FROM Contribucion WHERE IDU = p.IDU ORDER BY Fecha DESC LIMIT 1) as Fecha_Pub,
        
        COALESCE(SUM(rp.score_reac), 0) + COALESCE(SUM(cp.score_com), 0) as Puntaje_Total
    FROM Usuario u
    JOIN Publicacion p ON u.IDU = p.IDU
    
    LEFT JOIN ReaccionesPonderadas rp ON p.IDPub = rp.IDPub
    LEFT JOIN ComentariosPonderados cp ON p.IDPub = cp.IDPub
    
    WHERE COALESCE(rp.score_reac, 0) + COALESCE(cp.score_com, 0) > 0
    
    GROUP BY u.IDU, u.Nombre, p.IDPub
    ORDER BY Puntaje_Total DESC
    LIMIT 5;
    """
    
    top_posts = DatabaseConnector.execute_query(sql_top_influencers)

    for post in top_posts:
        influencer_id = post['IDU']
        product_id = post['IDProd'] 
        pub_date = post['Fecha_Pub']
        pub_id = post['IDPub']

        if not product_id:
            continue
            
        sql_sales = """
        SELECT 
            SUM(CASE WHEN Fecha BETWEEN DATE_SUB(%s, INTERVAL 14 DAY) AND %s THEN Cantidad ELSE 0 END) as Ventas_Antes,
            SUM(CASE WHEN Fecha BETWEEN %s AND DATE_ADD(%s, INTERVAL 14 DAY) THEN Cantidad ELSE 0 END) as Ventas_Despues
        FROM Compra
        WHERE IDProd = %s;
        """
        sales_data = DatabaseConnector.execute_query(sql_sales, (pub_date, pub_date, pub_date, pub_date, product_id))
        
        v_antes = sales_data[0]['Ventas_Antes'] or 0
        v_despues = sales_data[0]['Ventas_Despues'] or 0
        
        if v_antes > 0:
            incremento_pct = ((v_despues - v_antes) / v_antes) * 100
        else:
            incremento_pct = 100 if v_despues > 0 else 0

        sql_conversion = """
        SELECT 
            (COUNT(DISTINCT c.IDUC) / NULLIF((SELECT COUNT(DISTINCT IDU) FROM Reaccionar WHERE IDPub = %s), 0)) * 100 as Tasa_Conversion
        FROM Compra c
        JOIN Reaccionar r ON c.IDUC = r.IDU
        WHERE r.IDPub = %s 
          AND c.IDProd = %s
          AND c.Fecha >= r.Fecha; 
        """
        conv_data = DatabaseConnector.execute_query(sql_conversion, (pub_id, pub_id, product_id))
        tasa_conv = conv_data[0]['Tasa_Conversion'] or 0.0

        results.append({
            "Influencer": post['Nombre'],
            "Puntaje Impacto": float(post['Puntaje_Total']),
            "Planta Promocionada (ID)": product_id,
            "Fecha Publicación": pub_date,
            "Ventas Antes (2sem)": v_antes,
            "Ventas Después (2sem)": v_despues,
            "Incremento Ventas %": round(incremento_pct, 2),
            "Tasa Conversión %": round(tasa_conv, 2)
        })

    return results


def find_sellers_with_irregular_pricing():
    """q1 Encuentra vendedores con precios irregulares para el mismo producto."""
    query = """
SELECT 
    distinct v1.IDUV AS Vendedor
FROM Compra v1
JOIN Compra v2 ON 
    v1.IDUV = v2.IDUV    
WHERE 
    (v1.Precio >= v2.Precio * 1.3 OR v2.Precio >= v1.Precio * 1.3) and ABS(DATEDIFF(v1.Fecha, v2.Fecha)) <= 60
;
"""
    return DatabaseConnector.execute_query(query)


def find_polarized_sellers_ratings():
    """q2 Encuentra vendedores con calificaciones polarizadas (muchos 5 y 1 estrellas)."""
    query = """
SELECT com.IDUV,
COUNT(*) AS Total,
SUM(CASE WHEN com.Puntuacion = 5 OR com.Puntuacion = 1 THEN 1 ELSE 0 END) AS Puntuaciones_Polarizadas,
SUM(CASE WHEN com.Puntuacion IN (2, 3, 4) THEN 1 ELSE 0 END) AS Puntuaciones_Intermedias
FROM Compra com
WHERE com.Puntuacion IS NOT NULL
GROUP BY com.IDUV
HAVING Total * 0.85 <= Puntuaciones_Polarizadas AND Puntuaciones_Polarizadas*0.30 > Puntuaciones_Intermedias 
;
"""
    return DatabaseConnector.execute_query(query)

def find_sellers_with_exclusive_customers():
    """q3 Encuentra vendedores cuyos compradores son casi exclusivos o exclusivos."""
    query = """
SELECT  
    c.IDUV,
    CASE 
        WHEN cc.Vendedores_Diferentes = 1 THEN 'EXCLUSIVO'
        WHEN cc.Vendedores_Diferentes = 2 THEN 'CASI_EXCLUSIVO'
        ELSE 'NORMAL'
    END AS Tipo_Comprador
FROM Compra c
JOIN (
    SELECT 
        IDUC,
        COUNT(DISTINCT IDUV) AS Vendedores_Diferentes
    FROM Compra
    GROUP BY IDUC
) as cc ON c.IDUC = cc.IDUC
WHERE cc.Vendedores_Diferentes <= 2  
;
"""
    return DatabaseConnector.execute_query(query)