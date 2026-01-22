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
SELECT 
    c.IDProd,
    p.NombreComun AS Nombre_Planta,
    COUNT( CASE 
        WHEN rcc.Tipo IN ('Me gusta', 'Me encanta', 'Me divierte', 'Me asombra') 
        THEN rcc.IDU 
    END) AS reacciones_positivas,
    COUNT( rcc.IDU) AS total_reacciones
FROM Contribucion c
JOIN Planta p ON c.IDProd = p.IDProd
JOIN Contribucion_Foto cf ON c.IDProd = cf.IDProd AND c.Fecha = cf.Fecha
JOIN Tener_Foto tf ON tf.IDF = cf.IDF
JOIN Publicacion pub_foto ON tf.IDPub = pub_foto.IDPub
JOIN Contribucion_Video cv ON c.IDProd = cv.IDProd AND c.Fecha = cv.Fecha
JOIN Publicacion pub_video ON cv.IDV = pub_video.IDV
JOIN Reaccionar rcc ON (
    rcc.IDPub IN (pub_foto.IDPub, pub_video.IDPub)
)
GROUP BY c.IDProd, p.NombreComun
ORDER BY reacciones_positivas DESC
LIMIT 3;
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
SELECT
    u.IDU,
    u.Nombre,
    COUNT(DISTINCT cf.IDF) + COUNT(DISTINCT cv.IDV) AS Total_Multimedia_Ultimo_Anio,
    (COUNT(DISTINCT cf.IDF) + COUNT(DISTINCT cv.IDV)) / 12 AS Promedio_Mensual_Multimedia
FROM Usuario u
JOIN Contribucion c ON u.IDU = c.IDU
JOIN Contribucion_Foto cf ON c.IDProd = cf.IDProd AND c.Fecha = cf.Fecha
JOIN Contribucion_Video cv ON c.IDProd = cv.IDProd AND c.Fecha = cv.Fecha
WHERE year(c.Fecha) = year(curdate())
GROUP BY u.IDU, u.Nombre
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
 SELECT 
    v1.IDProd,
    v1.Nombre,
    v1.Anio,
    v1.Mes,
    v1.Total_Vendido AS Ventas_Mes_Actual,
    v2.Total_Vendido AS Ventas_Mes_Anterior
FROM (
    SELECT
        c.IDProd,
        p.Nombre,
        YEAR(c.Fecha) AS Anio,
        MONTH(c.Fecha) AS Mes,
        SUM(c.Cantidad) AS Total_Vendido
    FROM Compra c
    JOIN Producto p ON c.IDProd = p.IDProd
    WHERE YEAR(c.Fecha) = YEAR(CURDATE())-1
    GROUP BY c.IDProd, p.Nombre, YEAR(c.Fecha), MONTH(c.Fecha)
) v1
LEFT JOIN (
    SELECT
        c.IDProd,
        YEAR(c.Fecha) AS Anio,
        MONTH(c.Fecha) AS Mes,
        SUM(c.Cantidad) AS Total_Vendido
    FROM Compra c
    WHERE YEAR(c.Fecha) = YEAR(CURDATE())-1
    GROUP BY c.IDProd, YEAR(c.Fecha), MONTH(c.Fecha)
) v2 ON v1.IDProd = v2.IDProd 
    AND (
        (v1.Anio = v2.Anio AND v1.Mes = v2.Mes + 1) 
        OR (v1.Anio = v2.Anio + 1 AND v1.Mes = 1 AND v2.Mes = 12)  
    )
WHERE v1.Total_Vendido <= v2.Total_Vendido
ORDER BY v1.IDProd, v1.Anio, v1.Mes;
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
WITH CategoriaFavoritaAnual AS (
    SELECT 
        u.IDU,
        u.Nombre,
        YEAR(c.Fecha) AS Anio,
        p.Categoria,
        COUNT(*) AS Contribuciones,
        
        ROW_NUMBER() OVER (
            PARTITION BY u.IDU, YEAR(c.Fecha) 
            ORDER BY COUNT(*) DESC
        ) AS Posicion
    FROM Usuario u
    JOIN Contribucion c ON u.IDU = c.IDU
    JOIN Planta p ON c.IDProd = p.IDProd
    GROUP BY u.IDU, u.Nombre, YEAR(c.Fecha), p.Categoria
)
SELECT 
    a.IDU,
    a.Nombre,
    a.Anio AS Anio_Anterior,
    a.Categoria AS Categoria_Anterior,
    b.Anio AS Anio_Actual, 
    b.Categoria AS Categoria_Actual
FROM CategoriaFavoritaAnual a
JOIN CategoriaFavoritaAnual b 
    ON a.IDU = b.IDU 
    AND a.Anio = b.Anio - 1  
    AND a.Posicion = 1 
    AND b.Posicion = 1       
    AND a.Categoria <> b.Categoria  
ORDER BY a.IDU, a.Anio;
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
    results = []
    
    # 1. Top 5 influencers
    sql_top_influencers = """
    SELECT 
        u.IDU,
        u.Nombre,
        SUM(
            CASE 
                WHEN r.Tipo = 'Me gusta' THEN 1 
                WHEN r.Tipo = 'Me encanta' THEN 2 
                WHEN r.Tipo = 'Me asombra' THEN 1.5 
                ELSE 0 
            END
        ) + (COUNT(c.IDPub) * 2) as Puntaje_Total
    FROM Usuario u
    JOIN Publicacion p ON u.IDU = p.IDU
    LEFT JOIN Reaccionar r ON p.IDPub = r.IDPub
    LEFT JOIN Comentar c ON p.IDPub = c.IDPub
    GROUP BY u.IDU, u.Nombre
    HAVING Puntaje_Total > 0
    ORDER BY Puntaje_Total DESC
    LIMIT 5;
    """
    
    influencers = DatabaseConnector.execute_query(sql_top_influencers)
    
    for inf in influencers:
        influencer_id = inf['IDU']
        influencer_nombre = inf['Nombre']
        puntaje_total = inf['Puntaje_Total']
        
        # 2. Planta con la que más ha interactuado
        sql_planta_principal = f"""
        WITH InteraccionesPlantas AS (
            -- Publicaciones con fotos de plantas
            SELECT p.IDProd, COUNT(*) as cantidad
            FROM Publicacion pub
            JOIN Tener_Foto tf ON pub.IDPub = tf.IDPub
            JOIN Contribucion_Foto cf ON tf.IDF = cf.IDF
            JOIN Planta p ON cf.IDProd = p.IDProd
            WHERE pub.IDU = {influencer_id}
            GROUP BY p.IDProd
            
            UNION ALL
            
            -- Publicaciones con videos de plantas
            SELECT p.IDProd, COUNT(*) as cantidad
            FROM Publicacion pub
            JOIN Contribucion_Video cv ON pub.IDV = cv.IDV
            JOIN Planta p ON cv.IDProd = p.IDProd
            WHERE pub.IDU = {influencer_id}
            GROUP BY p.IDProd
            UNION ALL
            
            -- Compras del influencer
            SELECT p.IDProd, SUM(Cantidad) as cantidad
            FROM Compra c
            JOIN Planta p ON c.IDProd = p.IDProd
            WHERE c.IDUC = {influencer_id}
            GROUP BY p.IDProd
        )
        SELECT 
            p.IDProd,
            p.NombreComun,
            SUM(ip.cantidad) as total_interacciones
        FROM InteraccionesPlantas ip
        JOIN Planta p ON ip.IDProd = p.IDProd
        GROUP BY p.IDProd, p.NombreComun
        ORDER BY total_interacciones DESC
        LIMIT 1;
        """
        planta_data = DatabaseConnector.execute_query(sql_planta_principal)
        
        if not planta_data or not planta_data[0]['IDProd']:
            continue
            
        planta_id = planta_data[0]['IDProd']
        planta_nombre = planta_data[0]['NombreComun']
        
        # 3. Fechas de publicaciones recientes sobre esta planta
        sql_fechas_publicaciones = f"""
        SELECT DISTINCT c.Fecha
        FROM Publicacion p
        LEFT JOIN Tener_Foto tf ON p.IDPub = tf.IDPub
        LEFT JOIN Contribucion_Foto cf ON tf.IDF = cf.IDF
        LEFT JOIN Contribucion c ON cf.IDProd = c.IDProd AND cf.Fecha = c.Fecha
        WHERE p.IDU = {influencer_id}
          AND (c.IDProd = {planta_id} OR p.IDV IN (
              SELECT cv.IDV 
              FROM Contribucion_Video cv 
              WHERE cv.IDProd = {planta_id}
          ))
        ORDER BY c.Fecha DESC
        LIMIT 3;
        """
        
        fechas_pub = DatabaseConnector.execute_query(sql_fechas_publicaciones)
        
        ventas_antes = 0
        ventas_despues = 0
        
        if fechas_pub:
            # 4. Calcular ventas alrededor de cada publicación
            for fecha_obj in fechas_pub:
                fecha = fecha_obj['Fecha']
                
                sql_ventas = f"""
                SELECT 
                    COALESCE(SUM(CASE 
                        WHEN Fecha BETWEEN DATE_SUB('{fecha}', INTERVAL 14 DAY) AND '{fecha}'
                        THEN Cantidad ELSE 0 END), 0) as ventas_antes,
                    COALESCE(SUM(CASE 
                        WHEN Fecha BETWEEN '{fecha}' AND DATE_ADD('{fecha}', INTERVAL 14 DAY)
                        THEN Cantidad ELSE 0 END), 0) as ventas_despues
                FROM Compra
                WHERE IDProd = {planta_id};
                """
                
                ventas = DatabaseConnector.execute_query(sql_ventas)
                
                if ventas:
                    ventas_antes += ventas[0]['ventas_antes'] or 0
                    ventas_despues += ventas[0]['ventas_despues'] or 0
        
        # 5. Calcular incremento porcentual
        if ventas_antes > 0:
            incremento_pct = ((ventas_despues - ventas_antes) / ventas_antes) * 100
        else:
            incremento_pct = 100 if ventas_despues > 0 else 0
        
        # 6. Tasa de conversión simplificada
        sql_tasa_conversion = f"""
        WITH UsuariosReaccionaron AS (
    SELECT DISTINCT r.IDU
    FROM Reaccionar r
    JOIN Publicacion p ON r.IDPub = p.IDPub
    WHERE p.IDU = {influencer_id}
      AND p.IDPub IN (
          SELECT p2.IDPub
          FROM Publicacion p2
          LEFT JOIN Tener_Foto tf ON p2.IDPub = tf.IDPub
          LEFT JOIN Contribucion_Foto cf ON tf.IDF = cf.IDF
          LEFT JOIN Contribucion_Video cv ON p2.IDV = cv.IDV
          WHERE (cf.IDProd = {planta_id} OR cv.IDProd = {planta_id})
      )
),
UsuariosCompraron AS (
    SELECT DISTINCT c.IDUC
    FROM Compra c
    WHERE c.IDProd = {planta_id}
      AND c.IDUC IN (SELECT IDU FROM UsuariosReaccionaron)
      AND c.IDUC IN (
          SELECT r2.IDU
          FROM Reaccionar r2
          JOIN Publicacion p2 ON r2.IDPub = p2.IDPub
          WHERE p2.IDU = {influencer_id}
            AND c.Fecha >= r2.Fecha
            AND c.Fecha <= DATE_ADD(r2.Fecha, INTERVAL 30 DAY)
      )
)
        SELECT 
            CASE 
                WHEN (SELECT COUNT(*) FROM UsuariosReaccionaron) > 0 
                THEN (SELECT COUNT(*) FROM UsuariosCompraron) * 100.0 / 
                    (SELECT COUNT(*) FROM UsuariosReaccionaron)
                ELSE 0 
            END as tasa_conversion;
        """
        
        conv_data = DatabaseConnector.execute_query(sql_tasa_conversion)
        tasa_conv = conv_data[0]['tasa_conversion'] if conv_data and conv_data[0]['tasa_conversion'] else 0
        
        results.append({
            "Influencer": influencer_nombre,
            "Puntaje_Impacto": float(puntaje_total),
            "Planta_Promocionada_ID": planta_id,
            "Planta_Promocionada_Nombre": planta_nombre,
            "Ventas_Antes_2sem": ventas_antes,
            "Ventas_Despues_2sem": ventas_despues,
            "Incremento_Ventas_%": round(incremento_pct, 2),
            "Tasa_Conversion_%": round(tasa_conv, 2)
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