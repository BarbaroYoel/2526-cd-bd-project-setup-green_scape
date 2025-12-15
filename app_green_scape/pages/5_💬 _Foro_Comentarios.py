import streamlit as st
import pandas as pd

from queries.sql_comment_queries import (
    get_full_thread_sql, 
    get_available_users, 
    get_available_publications, 
    get_root_comments_for_pub, 
    insert_new_comment
)
from utils.database_connector import DatabaseConnector



def display_thread(hilo, id_pub_actual, root_id, users_map):
    st.subheader(f"🗣️ Hilo Raíz Seleccionado (ID: {root_id})")
    
    for comment in hilo:
        nivel = comment['Nivel']
        indent = "—" * (nivel * 2) 
        idcom = comment['IDCom']
        
        user_name = users_map.get(comment['IDU'], f"Usuario ID {comment['IDU']}")

        with st.expander(f"**{"--"} N{nivel}** | ID: {idcom} | Por: {user_name}", expanded=(nivel < 0)): 
            st.markdown(f"**Contenido:** {comment['Contenido']}")
            st.caption(f"Responde a ID: {comment['IDPadre'] if comment['IDPadre'] else id_pub_actual}")
            
            with st.form(key=f'form_reply_{idcom}'):
                st.markdown("**Responder a este comentario:**")
                
                reply_user_id = st.selectbox(
                    "Selecciona tu Usuario:", 
                    options=list(users_map.keys()), 
                    format_func=lambda x: users_map[x],
                    key=f'reply_user_{idcom}'
                )
                
                reply_content = st.text_area("Tu Respuesta:", key=f'reply_content_{idcom}', height=70)
                submit_reply = st.form_submit_button("Enviar Respuesta")
                
                if submit_reply and reply_content:
                    new_id = insert_new_comment(reply_content, reply_user_id, id_pub_actual, idcom)
                    if new_id:
                        st.success(f"Respuesta enviada exitosamente. Nuevo ID: {new_id}")
                        st.session_state['current_root_id'] = root_id 
                        st.rerun()


def handle_root_selection(root_id):
    """Función callback para cambiar el hilo raíz seleccionado."""
    st.session_state['current_root_id'] = root_id



def app_hilos_conversacion():
    st.set_page_config(page_title="Hilos de Conversación SQL", page_icon="💬", layout="wide")
    st.title("💬 Gestión de Hilos de Conversación ")
    st.caption("Selecciona una publicación y luego escoge el hilo raíz a visualizar.")
    st.markdown("---")

    users_map = get_available_users()
    publicaciones_map = get_available_publications()
    
    if not publicaciones_map:
        st.error("No se pudieron cargar publicaciones. Verifique su base de datos.")
        return

    opciones_display = list(publicaciones_map.values())
    
    if 'selected_pub_display' not in st.session_state:
        st.session_state['selected_pub_display'] = opciones_display[0]

    seleccion_display = st.selectbox(
        "Selecciona el contexto de la conversación:", 
        opciones_display, 
        key='pub_selector'
    )
    
    id_pub_seleccionada = next(
        (idpub for idpub, text in publicaciones_map.items() if text == seleccion_display), 
        list(publicaciones_map.keys())[0]
    )

    if st.session_state.get('last_pub_id') != id_pub_seleccionada:
        st.session_state['current_root_id'] = None
        st.session_state['last_pub_id'] = id_pub_seleccionada
    
    st.markdown("---")
    
    col_roots, col_visual, col_form = st.columns([1, 2, 1])

    with col_roots:
        st.header("Lista de Hilos")
        hilos_raiz = get_root_comments_for_pub(id_pub_seleccionada)
        
        if hilos_raiz:
            st.info(f"Hilos encontrados: {len(hilos_raiz)}")
            
            if st.session_state.get('current_root_id') is None:
                st.session_state['current_root_id'] = hilos_raiz[0]['IDCom']
            
            for root in hilos_raiz:
                root_id = root['IDCom']
                user_name = users_map.get(root['IDU'], f"ID {root['IDU']}")
                
                is_selected = (root_id == st.session_state.get('current_root_id'))
                
                label = f"**ID {root_id}** | {user_name}: {root['Snippet']}..."
                
                st.button(
                    label, 
                    key=f'select_root_{root_id}',
                    type="primary" if is_selected else "secondary",
                    on_click=handle_root_selection,
                    args=(root_id,)
                )

        else:
            st.warning("No hay hilos de conversación para esta publicación.")

    with col_visual:
        root_id_to_display = st.session_state.get('current_root_id')
        
        if root_id_to_display:
            try:
                hilo_completo = get_full_thread_sql(root_id_to_display)
                if hilo_completo:
                    display_thread(hilo_completo, id_pub_seleccionada, root_id_to_display, users_map)
                else:
                    st.info(f"Se encontró la raíz ID {root_id_to_display} pero la consulta recursiva no devolvió comentarios.")
                    
            except Exception as e:
                st.error(f"Error al cargar el hilo de conversación: {e}")
        else:
            st.warning("Selecciona un hilo raíz de la lista de la izquierda.")

    with col_form:
        st.header("➕ Nuevo Hilo")
        with st.form(key='form_new_thread'):
            new_user_id = st.selectbox(
                "Usuario:", 
                options=list(users_map.keys()), 
                format_func=lambda x: users_map[x],
                key='new_thread_user'
            )
            new_content = st.text_area("Contenido del Nuevo Hilo:", key='new_thread_content', height=100)
            submit_new = st.form_submit_button("Crear Hilo Raíz")
            
            if submit_new and new_content:
                new_root_id = insert_new_comment(new_content, new_user_id, id_pub_seleccionada, None)
                if new_root_id:
                    st.success(f"Nuevo hilo creado. ID: {new_root_id}")
                    st.session_state['current_root_id'] = new_root_id 
                    st.rerun()


if __name__ == "__main__":
    app_hilos_conversacion()