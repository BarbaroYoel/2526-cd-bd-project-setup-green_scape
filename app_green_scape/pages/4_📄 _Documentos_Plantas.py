import streamlit as st
import pandas as pd
from queries.plant_documents_queries import get_plant_documentation, get_available_plants 

st.set_page_config(page_title="Documentación Botánica", page_icon="📄", layout="wide")
st.title("🌿 Explorador de Documentación Jerárquica (MongoDB)")
st.markdown("---")

productos = get_available_plants()

if not productos:
    st.error("❌ ERROR: No se pudieron cargar las plantas disponibles. Por favor, verifique la conexión a MySQL y que la tabla 'Planta' esté poblada.")
    productos = [{'NombreComun': 'Planta Araña (Demo)', 'IDProd': 1}, {'NombreComun': 'Potos (Demo)', 'IDProd': 3}]
    st.info("Usando datos de demostración para el selector.")
    

opciones = {f"{p['NombreComun']} (ID: {p['IDProd']})": p['IDProd'] for p in productos}
seleccion = st.selectbox("Selecciona una Planta:", list(opciones.keys()))

id_planta = opciones.get(seleccion)

st.markdown("---")

if st.button("Buscar Documentación Detallada"):
    if id_planta is not None:
        documento_planta = get_plant_documentation(id_planta)

        if not documento_planta:
            st.warning(f"⚠️ Documentación no encontrada en MongoDB para la planta con ID {id_planta}.")
        else:
            st.success(f"Documentación encontrada para **{documento_planta.get('NombrePlanta')}**.")
            st.markdown("---")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                ficha_tecnica = documento_planta.get('FichaTecnica', {})
                st.header(f"📂 {ficha_tecnica.get('titulo', 'Ficha Técnica Principal')}")
                st.markdown(f"***ID de Producto: {id_planta}***")

                if ficha_tecnica:
                    datos_principales = {k: v for k, v in ficha_tecnica.items() if k != 'titulo'}
                    df_ficha = pd.DataFrame(
                        list(datos_principales.items()), 
                        columns=['Propiedad', 'Valor']
                    )
                    st.table(df_ficha.set_index('Propiedad'))
            
            with col2:
                secundarios = documento_planta.get('DocumentosSecundarios', [])
                st.header("🗂️ Documentos Complementarios")
                
                if secundarios:
                    st.info(f"Se encontraron {len(secundarios)} documentos secundarios.")
                    
                    for i, doc in enumerate(secundarios):
                        tipo = doc.get('tipo', 'Documento Secundario')
                        titulo = doc.get('titulo', 'Sin Título')
                        
                        with st.expander(f"**{tipo}:** {titulo}", expanded=(i < 0)):
                            
                            datos_especificos = {k: v for k, v in doc.items() if k not in ['tipo', 'titulo']}
                            
                            if datos_especificos:
                                df_secundario = pd.DataFrame(
                                    list(datos_especificos.items()), 
                                    columns=['Especificación', 'Detalle']
                                )
                                st.table(df_secundario.set_index('Especificación'))
                        st.markdown("---")
                else:
                    st.warning("Esta planta no tiene documentos complementarios cargados en MongoDB.")
