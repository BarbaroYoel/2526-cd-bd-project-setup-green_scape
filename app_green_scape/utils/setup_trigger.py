import sys
from utils.database_connector import DatabaseConnector

def setup_price_audit_trigger():
    print("--- ⚙️ Iniciando Configuración de Trigger de Auditoría de Precios ---")
    
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS Historial_Precios (
        IDA INT NOT NULL AUTO_INCREMENT,
        IDProd INT NOT NULL,
        Precio_Anterior FLOAT NOT NULL,
        Precio_Nuevo FLOAT NOT NULL,
        Porcentaje_Cambio FLOAT NOT NULL,
        Fecha_Cambio DATETIME NOT NULL,
        PRIMARY KEY (IDA),
        FOREIGN KEY cal_prod(IDProd) REFERENCES Producto(IDProd) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    """
    
    CREATE_TRIGGER_SQL = """
    CREATE TRIGGER IF NOT EXISTS tr_auditoria_precios_after_update
    AFTER UPDATE ON Producto
    FOR EACH ROW
    BEGIN
        DECLARE porcentaje FLOAT;
        
        -- Verificar si el precio realmente cambió
        IF OLD.Precio != NEW.Precio THEN
            -- Calcular porcentaje de cambio
            IF OLD.Precio = 0 THEN
                SET porcentaje = 100.00;
            ELSE
                SET porcentaje = ((NEW.Precio - OLD.Precio) / OLD.Precio) * 100;
            END IF;
            
            -- Insertar registro en la tabla de auditoría
            INSERT INTO Historial_Precios (
                IDProd,
                Precio_Anterior,
                Precio_Nuevo,
                Porcentaje_Cambio,
                Fecha_Cambio
            ) VALUES (
                OLD.IDProd,
                OLD.Precio,
                NEW.Precio,
                porcentaje,
                NOW()
            );
        END IF;
    END;
    """
    
    try:
        DatabaseConnector.execute_ddl_dml(CREATE_TABLE_SQL)
        print("   ✅ Tabla 'Historial_Precios' creada o verificada.")
        
        try:
            DatabaseConnector.execute_ddl_dml("DROP TRIGGER IF EXISTS tr_auditoria_precios_after_update;")
            print("   ✅ Trigger antiguo eliminado (si existía).")
        except Exception as e:
            print(f"   Advertencia al intentar DROP TRIGGER: {e}")

        DatabaseConnector.execute_ddl_dml(CREATE_TRIGGER_SQL)
        print("   ✅ Trigger 'tr_auditoria_precios_after_update' creado con éxito.")

    except Exception as e:
        print(f"--- ❌ ERROR FATAL en la configuración del Trigger: {e}")
        sys.exit(1)
        
    print("--- ✅ Configuración de Trigger Finalizada. ---")


if __name__ == '__main__':
    setup_price_audit_trigger()