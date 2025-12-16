import streamlit as st
import pandas as pd
import sys

from utils.database_connector import DatabaseConnector

if 'producto_id_persist' not in st.session_state:
    st.session_state.producto_id_persist = None


@st.cache_data(ttl=60)
def get_productos_con_precio():
    """Consulta la lista de productos con su precio actual."""
    query = """
    SELECT 
        IDProd,
        Nombre,
        Precio
    FROM Producto
    ORDER BY Nombre;
    """
    return DatabaseConnector.execute_query(query)

def update_producto_precio(product_id, new_price):
    """
    Actualiza el precio de un producto. 
    """
    query = "UPDATE Producto SET Precio = %s WHERE IDProd = %s;"
    return DatabaseConnector.execute_ddl_dml(query, (new_price, product_id))

@st.cache_data(ttl=5)
def get_historial_precios(product_id):
    """Consulta el historial de precios auditado por el Trigger."""
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

st.set_page_config(page_title="Gestor de Precios", page_icon="💰", layout="wide")
st.title("💰 Gestor de Precios de Productos")
st.markdown("Interfaz para modificar precios.")

productos = get_productos_con_precio()

if not productos:
    st.warning("No se encontraron productos en la base de datos (Tabla 'Producto').")
    st.stop()
    
df_productos = pd.DataFrame(productos)
df_productos['Etiqueta'] = df_productos.apply(
    lambda row: f"ID {row['IDProd']} | {row['Nombre']} (Actual: ${row['Precio']:.2f})", 
    axis=1
)
etiquetas = df_productos['Etiqueta'].tolist()

default_index = 0

if st.session_state.producto_id_persist is not None:
    persisted_id = st.session_state.producto_id_persist
    
    matching_row = df_productos[df_productos['IDProd'] == persisted_id]
    
    if not matching_row.empty:
        persisted_label = matching_row['Etiqueta'].iloc[0]
        try:
            default_index = etiquetas.index(persisted_label)
        except ValueError:
            pass 
        
    st.session_state.producto_id_persist = None 


col1, col2 = st.columns([1, 2])

with col1:
    
    selected_label = st.selectbox(
        "Seleccionar Producto:",
        etiquetas,
        index=default_index,
        key="selector_producto" 
    )
    

    selected_row = df_productos[df_productos['Etiqueta'] == selected_label].iloc[0]
    
    selected_id = int(selected_row['IDProd']) 
    precio_actual = selected_row['Precio']
    nombre_producto = selected_row['Nombre']

with col2:
    st.metric(f"Precio Actual de {nombre_producto}", f"${precio_actual:.2f}")



st.divider()
st.subheader(f"Cambiar Precio")

col_input, col_button = st.columns([1, 3])

with col_input:
    nuevo_precio = st.number_input(
        "Nuevo Precio:",
        min_value=0.01,
        value=precio_actual,
        step=0.5,
        format="%.2f",
        key=f"input_nuevo_precio_{selected_id}" 
    )

with col_button:
    st.write(" ") 
    if st.button(f"ACTUALIZAR PRECIO", use_container_width=True, type="primary"):
        if nuevo_precio == precio_actual:
            st.warning("El precio es idéntico al actual. No se ejecutará la actualización.")
        else:
            try:
                update_producto_precio(selected_id, nuevo_precio)
                
                st.session_state.producto_id_persist = selected_id 
                
                get_productos_con_precio.clear() 
                get_historial_precios.clear()
                
                st.success(f"Precio de '{nombre_producto}' actualizado a ${nuevo_precio:.2f}.")
                
            except Exception as e:
                st.error(f"Error al actualizar precio en DB: {e}")
            
            st.rerun() 


st.divider()
st.subheader("📚 Historial de Precios Auditado")
st.markdown(f"Registros de la tabla **`Historial_Precios`** generados automáticamente por el Trigger.")

historial_data = get_historial_precios(selected_id)

if historial_data:
    df_historial = pd.DataFrame(historial_data)
    
    df_historial['Precio_Anterior'] = df_historial['Precio_Anterior'].apply(lambda x: f"${x:.2f}")
    df_historial['Precio_Nuevo'] = df_historial['Precio_Nuevo'].apply(lambda x: f"${x:.2f}")
    df_historial['Porcentaje_Cambio'] = df_historial['Porcentaje_Cambio'].apply(
        lambda x: f"{'▲ +' if x > 0 else '▼ ' if x < 0 else '='}{x:.2f}%"
    )
    
    st.dataframe(
        df_historial,
        column_config={
            "IDA": "ID Auditoría",
            "Precio_Anterior": "Precio Anterior",
            "Precio_Nuevo": "Precio Nuevo",
            "Porcentaje_Cambio": "% Cambio",
            "Fecha_Cambio_Fmt": "Fecha y Hora"
        },
        hide_index=True,
        use_container_width=True
    )

else:
    st.info("No hay historial de cambios de precio para este producto en la tabla de auditoría.")