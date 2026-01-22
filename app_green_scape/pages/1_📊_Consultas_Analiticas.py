import streamlit as st
from queries import analytical_queries as aq
import pandas as pd

st.set_page_config(page_title="Consultas Analíticas", page_icon="📊", layout="wide")
st.header("📊 Consultas Analíticas")

query_options = {
    "a: Listar todos los productos disponibles": "get_all_products",
    "b: Top Publicaciones por Cantidad de Reacciones": "query_b_top_reactions",
    "c: Conteo de 'Me Gusta' por Producto": "query_c_likes_by_product",
    "d: Última Actividad de Usuario (Reacción/Cont.)": "query_d_last_activity_6m",
    "e: Publicaciones Positivas vs. Negativas": "query_e_pos_vs_neg_reactions",
    "f: Plantas con Contribuciones Consecutivas": "query_f_consecutive_contributions",
    
    "g: Promedio de actividad mensual": "get_monthly_activity_average",
    "h: Distribución de Usuarios por Rango de Edad": "query_h_age_distribution",
    "i: Productos con Patrones de Compra Estables": "query_i_stable_purchase_patterns",
    "j: Tendencias de Contribución por Clima": "contribution_trends_by_climate",
    "k: Cambio de preferencias de categorías": "get_category_preference_changes",
    "n: Vendedores Mejor Valorados (Compra)": "top_rated_sellers", 
    
    "l: Usuarios 'Raritos' (Compra vs. Gusto)": "query_l_raritos_compra_vs_gusto",
    "m: Usuarios sin Contenido Multimedia en Pub.": "query_m_users_without_multimedia",
    "p: Influencers y su impacto en Ventas": "analyze_influencers_impact",
    "q: Reporte de Vendedores Sospechosos (Detección de Fraude)": "get_seller_anomaly_report",
}

selected_query = st.selectbox("Selecciona una consulta:", list(query_options.keys()))

if st.button("Ejecutar Consulta"):
    try:
        with st.spinner("Ejecutando consulta..."):
            func_name = query_options[selected_query]
            resultados = getattr(aq, func_name)()

        if resultados:
            df = pd.DataFrame(resultados)
            st.success(f"✅ Consulta ejecutada exitosamente. {len(df)} registros encontrados.")
            st.dataframe(df, use_container_width=True)

        else:
            st.warning("⚠️ No se encontraron resultados para esta consulta.")
    except Exception as e:
        st.error(f"❌ Error al ejecutar la consulta: {str(e)}")
        st.info("Verifica la conexión a la base de datos y la estructura de las tablas.")