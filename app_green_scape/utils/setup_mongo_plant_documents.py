from utils.mongo_connector import MongoConnector

def initialize_mongo_plant_documents():
    coleccion = MongoConnector.get_collection(MongoConnector.COLLECTION_PLANTAS)
    if coleccion is None: 
        print("No se puede conectar a MongoDB para insertar datos.")
        return

    deleted = coleccion.delete_many({}) 
    print(f"Limpieza: Se eliminaron {deleted.deleted_count} documentos de la colección '{coleccion.name}'.")
    
    documentos_plantas = [
        {
            "IDProd": 1, 
            "NombrePlanta": "Planta Araña",
            "FichaTecnica": {"titulo": "Ficha Técnica Chlorophytum Comosum", "luz": "Indirecta Brillante", "temperatura": "18-24°C", "TipoSuelo": "Arenoso"},
            "DocumentosSecundarios": [
                {
                    "tipo": "Certificado Fitosanitario", "titulo": "Sanidad General Lote A-2024", 
                    "estado": "Libre de pulgón", "fecha_inspeccion": "2024-03-01", "validez_meses": 12
                },
                {
                    "tipo": "Guía de Riego Estacional", "titulo": "Riego para Climas Templados", 
                    "verano": "Mantener húmedo", "invierno": "Reducir a la mitad", "sensibilidad": "Cloro"
                },
                {
                    "tipo": "Manual de Tratamiento de Plagas", "titulo": "Control de Hongos", 
                    "plaga_comun": "Oídio", "tratamiento_quimico": "Fungicida Azufre", "preventivo": "Buena ventilación"
                }
            ]
        },
        {
            "IDProd": 2, 
            "NombrePlanta": "Planta Serpiente",
            "FichaTecnica": {"titulo": "Ficha Técnica Sansevieria Trifasciata", "luz": "Poca o Indirecta", "riego": "Bajo", "Categoria": "Ornamental"},
            "DocumentosSecundarios": [
                {
                    "tipo": "Historial de Crecimiento", "titulo": "Crecimiento de Hojas Nuevas", 
                    "promedio_anual_hojas": 4, "altura_actual_cm": 150, "fecha_trasplante": "2023-09-01"
                },
                {
                    "tipo": "Análisis de Suelo", "titulo": "Requerimientos de Drenaje", 
                    "ph_optimo": "6.0-7.0", "drenaje_requerido": "Extremo", "componente_clave": "Perlita"
                },
                {
                    "tipo": "Manual de Tratamiento de Plagas", "titulo": "Combate de Cochinilla", 
                    "sintomas": "Manchas pegajosas", "remedio_natural": "Aceite de Neem", "aplicacion": "No mojar hojas"
                }
            ]
        },
        {
            "IDProd": 3, 
            "NombrePlanta": "Potos",
            "FichaTecnica": {"titulo": "Ficha Técnica Epipremnum Aureum", "TipoSuelo": "Arcilloso", "propagacion": "Esquejes de tallo", "HorasLuz": 5},
            "DocumentosSecundarios": [
                {
                    "tipo": "Certificado Fitosanitario", "titulo": "Certificado de No Toxicidad", 
                    "uso": "Interior", "advertencia": "Tóxico si se ingiere", "ID_lote_madre": "POTOS-2022"
                },
                {
                    "tipo": "Guía de Riego Estacional", "titulo": "Riego en Interiores", 
                    "verano": "Cuando la capa superior esté seca", "invierno": "Cada 10 días", "temperatura_agua": "Ambiente"
                },
                {
                    "tipo": "Análisis de Suelo", "titulo": "Fertilización Trimestral", 
                    "frecuencia_fertilizante": "Trimestral", "tipo_fertilizante": "Líquido 20-20-20", "recomendacion_nutriente": "Nitrógeno alto"
                }
            ]
        },
        {
            "IDProd": 4, 
            "NombrePlanta": "Planta ZZ",
            "FichaTecnica": {"titulo": "Ficha Técnica Zamioculcas Zamiifolia", "Categoria": "Ornamental", "MililitrosAgua": 120, "TipoSuelo": "Arcilloso"},
            "DocumentosSecundarios": [
                {
                    "tipo": "Historial de Crecimiento", "titulo": "Monitoreo de Rizomas", 
                    "tasa_crecimiento_anual": "Lenta", "rizomas_activos": 5, "fecha_revisión_rizomas": "2024-01-01"
                },
                {
                    "tipo": "Certificado Fitosanitario", "titulo": "Declaración de Resistencia", 
                    "resistencia_sequía": "Alta", "resistencia_plagas": "Muy alta", "fecha_revision": "2023-11-15"
                },
                {
                    "tipo": "Guía de Riego Estacional", "titulo": "Riego Mínimo", 
                    "instrucción_clave": "Dejar secar totalmente", "invierno": "Cada 3-4 semanas", "error_común": "Exceso de riego"
                }
            ]
        },
        {
            "IDProd": 5, 
            "NombrePlanta": "Filodendro",
            "FichaTecnica": {"titulo": "Ficha Técnica Philodendron Spp", "HorasLuz": 5, "TipoSuelo": "Limoso", "NombreCientifico": "Philodendron Spp"},
            "DocumentosSecundarios": [
                {
                    "tipo": "Manual de Tratamiento de Plagas", "titulo": "Tratamiento de Trips", 
                    "sintomas": "Rastros plateados", "producto_recomendado": "Insecticida sistémico", "frecuencia_aplicacion": "2 semanas"
                },
                {
                    "tipo": "Historial de Crecimiento", "titulo": "Desarrollo del Tallado", 
                    "patrón_crecimiento": "Enredadera", "longitud_actual_cm": 250, "potencial_trepador": True
                },
                {
                    "tipo": "Análisis de Suelo", "titulo": "Revisión de Sustrato Orgánico", 
                    "porcentaje_turba": 50, "porcentaje_perlita": 20, "recomendacion_riego": "Agua de lluvia"
                }
            ]
        }
    ]
    
    result = coleccion.insert_many(documentos_plantas)
    print(f"Documentos de MongoDB insertados: {len(result.inserted_ids)}")

if __name__ == '__main__':
    initialize_mongo_plant_documents()