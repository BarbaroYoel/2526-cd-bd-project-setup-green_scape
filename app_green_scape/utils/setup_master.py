from utils.setup_mongo_plant_documents import initialize_mongo_plant_documents
from utils.setup_sql_comments import setup_sql_comments_db 
from utils.setup_db_procedure_definition import setup_stored_procedure 
from utils.setup_trigger import setup_price_audit_trigger


def run_all_setup():
  
    try:
        print("-> 1. Inicializando documentos de plantas en MongoDB...")
        initialize_mongo_plant_documents()
        
        print("-> 2. Configurando Procedimientos Almacenados en SQL...")
        setup_stored_procedure()
        
        print("-> 3. Configurando tabla de Comentarios en SQL...")
        setup_sql_comments_db()
        
        print("-> 4. Configurando Trigger de Auditoría SQL...")
        setup_price_audit_trigger() 

        print("   ✅ CONFIGURACIÓN FINALIZADA CON ÉXITO.")
        
    except Exception as e:
        print(f"   ❌ ERROR FATAL DURANTE EL SETUP: {e}")


if __name__ == '__main__':
    run_all_setup()