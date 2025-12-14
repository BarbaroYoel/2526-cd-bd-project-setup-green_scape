import streamlit as st
from queries import analytical_queries as aq
import pandas as pd

st.header("📊 Consultas Analíticas")

query_options = {
    "3.a: Listar todos los productos disponibles": "get_all_products",
    "3.g: Promedio de actividad mensual": "get_monthly_activity_average",
    "3.k: Cambio de preferencias": "get_category_preference_changes",
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