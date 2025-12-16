import streamlit as st
import pandas as pd
from datetime import datetime
import time 

from queries.sql_comment_queries import (
    get_full_thread_sql, 
    get_root_comments_for_pub,
    insert_new_comment_sql as insert_sql,
    delete_comment_sql ,
    get_root_comments_for_pub,
    get_available_publications
)
from queries.mongo_comment_queries import (
    get_full_thread_mongo, 
    insert_new_comment_mongo as insert_mongo,
    delete_comment_mongo ,
    get_root_comments_for_pub_mongo
)
from utils.database_connector import DatabaseConnector 
from utils.mongo_connector import MongoConnector
from utils.setup_comments_to_mongo import migrate_comments 


@st.cache_data(ttl=60) 
def get_sql_roots_cached(id_pub):
    return get_root_comments_for_pub(id_pub)


@st.cache_data(ttl=300)
def get_available_publications_cached(): 
    try:
        return get_available_publications()
    except Exception as e:
        st.error(f"❌ ERROR: No se pudieron cargar publicaciones. Error: {e}")
        return {} 


@st.cache_data(ttl=60) 
def get_mongo_roots_cached(id_pub):
    return get_root_comments_for_pub_mongo(id_pub)

def app_comparacion_db():
    st.set_page_config(page_title="MySQL vs. Mongo Comentarios", page_icon="⚔️", layout="wide")
    st.title("⚔️ Comparación de Rendimiento: Hilos de Comentarios")
    st.markdown("Mide la eficiencia de la lectura recursiva (CTE en SQL) frente a la consulta por ID Raíz (NoSQL).")

    time_sql_read = 9999.0
    time_mongo_read = 9999.0
    time_sql_write = 9999.0
    time_mongo_write = 9999.0


    if DatabaseConnector.get_connection() is None or MongoConnector.get_client() is None:
        st.error("❌ Error: Por favor, verifique las conexiones a MySQL y MongoDB.")
        return
    
    st.subheader("⚙️ Configuración de la Prueba")
    
    col_pub, col_sync = st.columns([3, 1])

    with col_pub:
        publicaciones_map = get_available_publications_cached()
        if not publicaciones_map: st.stop()
            
        opciones_display = list(publicaciones_map.values())
        seleccion_display = st.selectbox("1. Selecciona la Publicación a Analizar:", opciones_display)
        id_pub_seleccionada = next((idpub for idpub, text in publicaciones_map.items() if text == seleccion_display))
        
    with col_sync:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        if st.button("Sincronizar Datos (SQL -> Mongo)", help="Ejecuta migrate_comments() para que los hilos existan en ambas bases."):
            try:
                migrate_comments()
                get_sql_roots_cached.clear()
                st.success("✅ ¡Migración completada! Datos listos.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error durante la migración: {e}")

    sql_roots = get_sql_roots_cached(id_pub_seleccionada) 
    mongo_roots = get_mongo_roots_cached(id_pub_seleccionada)

    if not sql_roots or not mongo_roots:
        st.warning("No se encontraron hilos raíz comparables. Sincronice los datos arriba.")
        st.stop()
        
    sql_root_map = {r['IDCom']: f"ID {r['IDCom']} | {r['Snippet']}..." for r in sql_roots}
    
    selected_root_sql = st.selectbox(
        "2. Selecciona el Hilo Raíz para Pruebas (SQL):", 
        list(sql_root_map.keys()), 
        format_func=lambda x: sql_root_map[x]
    )
    
    mongo_match = next((r['IDCom'] for r in mongo_roots if str(r['IDCom']) == str(selected_root_sql)), mongo_roots[0]['IDCom'])
    selected_root_mongo = mongo_match

    st.info(f"Hilo SQL a probar: **ID {selected_root_sql}** | Hilo Mongo asociado: **ID {selected_root_mongo}**")


    st.markdown("---")
    
    st.header("⏱️ Resultados de la Medición")

    if st.button("Ejecutar Pruebas de Rendimiento (Lectura y Escritura)", type="primary"):
        
        st.subheader("1. Lectura de Hilo Completo (Velocidad de Query)")
        
        start_sql_read = time.perf_counter()
        hilo_sql = get_full_thread_sql(selected_root_sql)
        end_sql_read = time.perf_counter()
        time_sql_read = (end_sql_read - start_sql_read) * 1000

        start_mongo_read = time.perf_counter()
        hilo_mongo = get_full_thread_mongo(selected_root_mongo)
        end_mongo_read = time.perf_counter()
        time_mongo_read = (end_mongo_read - start_mongo_read) * 1000

        df_read = pd.DataFrame({
            "Base de Datos": ["MySQL (CTE Recursiva)", "MongoDB (IDRaiz + Ordenamiento App)"],
            "Tiempo (ms)": [f"{time_sql_read:.3f}", f"{time_mongo_read:.3f}"],
            "Nº Comentarios": [len(hilo_sql), len(hilo_mongo)]
        })
        st.dataframe(df_read, use_container_width=True)
        st.markdown("---")
        
        st.subheader("2. Escritura de Respuesta (Costo de Inserción)")
        st.caption("⚠️ **Los comentarios de prueba se eliminan inmediatamente** (pruebas transitorias).")

        target_comment_sql = hilo_sql[-1]['IDCom'] if hilo_sql else selected_root_sql
        target_comment_mongo = hilo_mongo[-1]['IDCom'] if hilo_mongo else selected_root_mongo
        
        test_user_id = 1 
        test_content = f"Prueba de escritura a las {datetime.now().strftime('%H:%M:%S')}"
        
        col_sql_write, col_mongo_write = st.columns(2)

        with col_sql_write:
            st.markdown("##### MySQL")
            start_sql_write = time.perf_counter()
            new_id_sql = insert_sql(test_content, test_user_id, id_pub_seleccionada, target_comment_sql)
            end_sql_write = time.perf_counter()
            time_sql_write = (end_sql_write - start_sql_write) * 1000
            
            st.metric("Tiempo Escritura (ms)", f"{time_sql_write:.3f}")
            
            if new_id_sql: delete_comment_sql(new_id_sql)


        with col_mongo_write:
            st.markdown("##### MongoDB")
            start_mongo_write = time.perf_counter()
            new_id_mongo = insert_mongo(test_content, test_user_id, id_pub_seleccionada, target_comment_mongo)
            end_mongo_write = time.perf_counter()
            time_mongo_write = (end_mongo_write - start_mongo_write) * 1000
            
            st.metric("Tiempo Escritura (ms)", f"{time_mongo_write:.3f}")
            
            if new_id_mongo: delete_comment_mongo(new_id_mongo)

        
        st.success("✅ Pruebas de rendimiento completadas y datos de prueba eliminados.")
        get_sql_roots_cached.clear() 
        
        st.session_state['time_sql_read'] = time_sql_read
        st.session_state['time_mongo_read'] = time_mongo_read
        st.session_state['time_sql_write'] = time_sql_write
        st.session_state['time_mongo_write'] = time_mongo_write
    
    time_sql_read = st.session_state.get('time_sql_read', time_sql_read)
    time_mongo_read = st.session_state.get('time_mongo_read', time_mongo_read)
    time_sql_write = st.session_state.get('time_sql_write', time_sql_write)
    time_mongo_write = st.session_state.get('time_mongo_write', time_mongo_write)


    st.markdown("---")
    st.header("📊 Comparación de Diseño y Capacidades")
    
    if time_sql_write < 9999.0 and time_mongo_write < 9999.0:
        escritura_sql_display = f"Lento ({time_sql_write:.3f} ms)"
        escritura_mongo_display = f"Rápido ({time_mongo_write:.3f} ms)"
        
        if time_mongo_write < time_sql_write:
            desc_escritura_sql = f"Lento (Requiere COMMIT, {time_sql_write:.3f} ms)."
            desc_escritura_mongo = f"Rápido (find + INSERT, {time_mongo_write:.3f} ms). Superior en esta prueba."
            conclusion_escritura = "MongoDB fue significativamente más rápido en la escritura en este entorno."
        else:
            desc_escritura_sql = f"Rápido (INSERT simple, {time_sql_write:.3f} ms)."
            desc_escritura_mongo = f"Más Lento (find + INSERT, {time_mongo_write:.3f} ms)."
            conclusion_escritura = "MySQL fue más rápido en la escritura, como se espera por la sencillez de su INSERT."
            
        desc_lectura_sql = f"Lento ({time_sql_read:.3f} ms)"
        desc_lectura_mongo = f"Rápido ({time_mongo_read:.3f} ms)"
    else:
        desc_escritura_sql = "Rápido (INSERT simple)"
        desc_escritura_mongo = "Más Lento (find + INSERT + Lógica App)"
        desc_lectura_sql = "Lento, requiere JOIN/Recursión"
        desc_lectura_mongo = "Rápido (un solo find)"
        conclusion_escritura = "Ejecute las pruebas para ver el rendimiento real en su entorno."


    comparacion_data = {
        "Aspecto": [
            "Mecanismo de Consulta de Hilo",
            "Velocidad de Lectura (Hilo Completo)",
            "Costo de Escritura (Crear Respuesta)",
            "Integridad Referencial (FKs)",
            "Lugar de la Lógica de Hilos"
        ],
        "Relacional (MySQL/CTE)": [
            "Consulta Recursiva (CTE) ",
            desc_lectura_sql,
            desc_escritura_sql,
            "Alta: Garantizada por Claves Foráneas.",
            "SQL (en la definición de la CTE)."
        ],
        "Documental (MongoDB/IDRaiz)": [
            "Consulta por Campo Indexado (`IDRaiz`) ",
            desc_lectura_mongo,
            desc_escritura_mongo,
            "Baja: Depende completamente de la aplicación.",
            "Python (al insertar y ordenar los resultados)."
        ]
    }
    
    df_comparacion = pd.DataFrame(comparacion_data)
    df_comparacion = df_comparacion.set_index("Aspecto")
    st.table(df_comparacion)
    


if __name__ == "__main__":
    app_comparacion_db()