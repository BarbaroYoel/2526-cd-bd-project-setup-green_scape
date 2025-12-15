import streamlit as st
from queries import user_queries as uq
import pandas as pd
from datetime import date

st.set_page_config(page_title="Panel Usuario", page_icon="👤", layout="wide")
st.header("👤 Panel Usuario")

st.subheader("Análisis de Actividad de Usuario")
st.write("Selecciona un usuario y un período para analizar su actividad en la plataforma.")

users = uq.get_users()
if users:
    user_options = {f"{user['Nombre']} (ID: {user['IDU']})": user['IDU'] for user in users}
    selected_user = st.selectbox("Selecciona un Usuario", list(user_options.keys()))
    idu = user_options[selected_user]
else:
    st.error("No se pudieron cargar los usuarios.")
    idu = None

col1, col2 = st.columns(2)
with col1:
    fecha_inicial = st.date_input("Fecha Inicial")
with col2:
    fecha_final = st.date_input("Fecha Final")

if st.button("Analizar Actividad"):
    if idu and fecha_inicial <= fecha_final:
        try:
            results = uq.analisis_usuario(idu, str(fecha_inicial), str(fecha_final))
            if results:
                result = results[0] 
                st.success("Análisis completado.")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Publicaciones", result.get('total_publicaciones', 0))
                    st.metric("Total Comentarios", result.get('total_comentarios', 0))
                with col2:
                    st.metric("Reacciones Dadas", result.get('reacciones_dadas', 0))
                    st.metric("Reacciones Recibidas", result.get('reacciones_recibidas', 0))
                with col3:
                    st.metric("Total Compras", result.get('total_compras', 0))
                    st.metric("Monto Gastado", f"${result.get('monto_gastado', 0):.2f}")
                
                st.metric("Total Contribuciones", result.get('total_contribuciones', 0))
                
                st.subheader("Plantas Más Compradas y Contribuidas")
                st.write(f"**Planta Más Comprada:** {result.get('planta_mas_comprada', 'N/A')}")
                st.write(f"**Planta Más Contribuida:** {result.get('planta_mas_contribuida', 'N/A')}")
            else:
                st.warning("No se encontraron datos para el período seleccionado.")
        except Exception as e:
            st.error(f"Error al realizar el análisis: {str(e)}")
    else:
        st.error("Selecciona un usuario válido y asegúrate de que la fecha inicial sea anterior o igual a la final.")