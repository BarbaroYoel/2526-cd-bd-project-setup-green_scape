from utils.database_connector import DatabaseConnector

def get_all_products():
    """a: Listar todos los productos disponibles"""
    query = """
    SELECT *
    FROM Producto
    ORDER BY Nombre;
    """
    return DatabaseConnector.execute_query(query)

def query_b_top_reactions():
    """b: Publicaciones con mayor cantidad de Reacciones"""
    query = """
SELECT 
    p.Texto AS Publicacion, 
    u.Nombre AS Autor, 
    COUNT(r.IDPub) AS Total_Reacciones
FROM Publicacion p
JOIN Usuario u ON p.IDU = u.IDU
LEFT JOIN Reaccionar r ON p.IDPub = r.IDPub
GROUP BY p.IDPub, u.Nombre
ORDER BY Total_Reacciones DESC ;
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
SELECT 
    u.Nombre, 
    u.Email,
    u.DireccionParticular,
    MAX(CASE 
        WHEN actividad.Fecha >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH) THEN actividad.Fecha 
        ELSE NULL 
    END) AS Ultima_Actividad_Reciente
FROM Usuario u
LEFT JOIN (
    SELECT IDU, Fecha FROM Contribucion
    UNION ALL
    SELECT IDU, Fecha FROM Reaccionar
) AS actividad ON u.IDU = actividad.IDU
GROUP BY u.IDU, u.Nombre, u.Email, u.DireccionParticular
ORDER BY Ultima_Actividad_Reciente DESC;
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
        SELECT DISTINCT IDProd, YEAR(Fecha) AS Anio, MONTH(Fecha) AS Mes
        FROM Contribucion
    ),
    CalculoConsecutivo AS (
        SELECT IDProd, Anio, Mes,
               LAG(Anio) OVER (PARTITION BY IDProd ORDER BY Anio, Mes) AS Anio_Ant,
               LAG(Mes) OVER (PARTITION BY IDProd ORDER BY Anio, Mes) AS Mes_Ant
        FROM MesesDeContribucion
    )
    SELECT DISTINCT p.NombreComun
    FROM CalculoConsecutivo c
    JOIN Planta p ON c.IDProd = p.IDProd
    WHERE (c.Anio = c.Anio_Ant AND c.Mes = c.Mes_Ant + 1)
       OR (c.Anio = c.Anio_Ant + 1 AND c.Mes = 1 AND c.Mes_Ant = 12)
    ORDER BY p.NombreComun;
    """
    return DatabaseConnector.execute_query(query)

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
    CONCAT(FLOOR((TIMESTAMPDIFF(YEAR, FechaDeNacimiento, CURDATE()) - 1) / 10) * 10 + 1, 
           '-', 
           FLOOR((TIMESTAMPDIFF(YEAR,FechaDeNacimiento, CURDATE()) - 1) / 10) * 10 + 10) AS rango_edad,
    COUNT(*) AS cantidad_usuarios,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Usuario), 2) AS porcentaje
FROM Usuario
GROUP BY rango_edad
ORDER BY MIN(FechaDeNacimiento) DESC;
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
    WITH PopularidadPorClima AS (
        SELECT 
            cl.Tipo AS TipoClima,
            p.NombreComun,
            COUNT(c.IDProd) AS Total_Contribuciones
        FROM Clima cl
        JOIN Planta p ON cl.IDC = p.IDC
        JOIN Contribucion c ON p.IDProd = c.IDProd
        GROUP BY cl.Tipo, p.NombreComun
    ),
    RankingClima AS (
        SELECT 
            TipoClima,
            NombreComun,
            Total_Contribuciones,
            RANK() OVER (PARTITION BY TipoClima ORDER BY Total_Contribuciones DESC) AS Posicion
        FROM PopularidadPorClima
    )
    SELECT 
        TipoClima AS Clima, 
        NombreComun AS Planta_Mas_Popular, 
        Total_Contribuciones
    FROM RankingClima
    WHERE Posicion = 1
    ORDER BY Total_Contribuciones DESC;
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
def query_l_raritos_compra_vs_gusto():
    """l: Usuarios que Compran Productos que No les Gustan ('Raritos')"""
    query = """
    WITH Compras_Categorizadas AS (
        SELECT 
            c.IDUC AS IDU,
            COUNT(CASE WHEN g.IDProd IS NULL THEN 1 END) AS Compras_Sin_Gusto,
            COUNT(CASE WHEN g.IDProd IS NOT NULL THEN 1 END) AS Compras_Con_Gusto
        FROM Compra c
        LEFT JOIN Gustar g ON c.IDUC = g.IDU AND c.IDProd = g.IDProd
        GROUP BY c.IDUC
    )
    SELECT 
        u.Nombre, 
        u.Email, 
        cc.Compras_Sin_Gusto, 
        cc.Compras_Con_Gusto
    FROM Compras_Categorizadas cc
    JOIN Usuario u ON cc.IDU = u.IDU
    WHERE cc.Compras_Sin_Gusto > cc.Compras_Con_Gusto
    ORDER BY cc.Compras_Sin_Gusto DESC;
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

def top_rated_sellers():
    """n: Vendedores Mejor Valorados (Usando la tabla Compra)"""
    query="""
        SELECT 
        u.Nombre, 
        u.Email, 
        u.DireccionParticular,
        COUNT(c.IDProd) AS Total_Productos_Vendidos,
        ROUND(AVG(c.Puntuacion), 2) AS Calificacion_Promedio
    FROM Usuario u
    JOIN Compra c ON u.IDU = c.IDUV
    WHERE c.Puntuacion IS NOT NULL
    GROUP BY u.IDU, u.Nombre, u.Email, u.DireccionParticular
    ORDER BY Calificacion_Promedio DESC, Total_Productos_Vendidos DESC
    LIMIT 5;
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


def get_seller_anomaly_report():
    """q: Detección de patrones de comportamiento anómalo en vendedores"""
    query = """
    WITH Sospecha_Precios AS (
        SELECT IDUV, 'Precios Inestables (>30%)' AS Evidencia, 10 AS Puntos
        FROM Compra
        GROUP BY IDUV, IDProd
        HAVING (MAX(Precio) - MIN(Precio)) / NULLIF(MIN(Precio), 0) > 0.3
    ),
    Sospecha_Reviews AS (
        SELECT IDUV, 'Ratings Polarizados (1 y 5)' AS Evidencia, 30 AS Puntos
        FROM Compra
        WHERE Puntuacion IS NOT NULL
        GROUP BY IDUV
        HAVING SUM(CASE WHEN Puntuacion IN (1, 5) THEN 1 ELSE 0 END) / COUNT(*) > 0.8
        AND COUNT(*) > 5
    ),
    Sospecha_Clientes AS (
        SELECT v.IDUV, 'Clientes Exclusivos (Posible Manipulación)' AS Evidencia, 40 AS Puntos
        FROM Compra v
        JOIN (
            SELECT IDUC
            FROM Compra
            GROUP BY IDUC
            HAVING COUNT(DISTINCT IDUV) = 1
        ) c_excl ON v.IDUC = c_excl.IDUC
        GROUP BY v.IDUV
        HAVING COUNT(DISTINCT v.IDUC) / (SELECT COUNT(DISTINCT IDUC) FROM Compra WHERE IDUV = v.IDUV) > 0.5
    ),
    Sospecha_Volumen AS (
        SELECT v.IDUV, 'Volumen Anómalo (3x Promedio)' AS Evidencia, 20 AS Puntos
        FROM Compra v
        JOIN (
            SELECT IDProd, COUNT(*) as Promedio_Ventas
            FROM Compra
            GROUP BY IDProd
        ) promedios ON v.IDProd = promedios.IDProd
        GROUP BY v.IDUV, v.IDProd
        -- CORRECCIÓN: Usamos MAX() para que SQL reconozca la columna en el HAVING
        HAVING COUNT(*) > (MAX(promedios.Promedio_Ventas) * 3)
    )
    SELECT 
        u.Nombre AS Vendedor,
        u.Email,
        (COALESCE(p.Puntos, 0) + COALESCE(r.Puntos, 0) + COALESCE(c.Puntos, 0) + COALESCE(vol.Puntos, 0)) AS Indice_Sospecha,
        CONCAT_WS(' | ', p.Evidencia, r.Evidencia, c.Evidencia, vol.Evidencia) AS Evidencias_Detectadas
    FROM Usuario u
    LEFT JOIN Sospecha_Precios p ON u.IDU = p.IDUV
    LEFT JOIN Sospecha_Reviews r ON u.IDU = r.IDUV
    LEFT JOIN Sospecha_Clientes c ON u.IDU = c.IDUV
    LEFT JOIN Sospecha_Volumen vol ON u.IDU = vol.IDUV
    WHERE p.IDUV IS NOT NULL OR r.IDUV IS NOT NULL OR c.IDUV IS NOT NULL OR vol.IDUV IS NOT NULL
    ORDER BY Indice_Sospecha DESC;
    """
    return DatabaseConnector.execute_query(query)