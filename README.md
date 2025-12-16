# 🌿 GreenScape - Plataforma de Análisis de Datos

Plataforma integral de análisis construida con Streamlit, MySQL y MongoDB para gestionar datos de usuarios, productos, comentarios y generar insights analíticos.

## 📁 Estructura

```
app_green_scape/
├── 🌿_Green_Scape.py              # Página principal
├── config/                         # Configuraciones DB
├── queries/                        # Consultas SQL y MongoDB
├── pages/                          # 6 secciones principales
├── utils/                          # Conectores y utilidades
└── notebooks/                      # Análisis Jupyter
```

## 📋 Requisitos Previos

- Python 3.8+
- Docker y Docker Compose
- pip

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Iniciar servicios (MySQL + MongoDB)

```bash
docker-compose up -d
```

**Credenciales:**
- MySQL: usuario `greenscape_user` / contraseña `greenscape_pass`
- MongoDB: usuario `root` / contraseña `mongo_pass`

### 3. Ejecutar setup inicial

⚠️ **IMPORTANTE: Este paso debe ejecutarse UNA SOLA VEZ**

```bash
cd app_green_scape
python utils/setup_master.py
```

Este script ejecuta automáticamente:
- Inicializa documentos de plantas en MongoDB
- Configura procedimientos almacenados en MySQL
- Crea tabla de comentarios en SQL
- Configura triggers de auditoría de precios

> **Nota**: Solo ejecutar la primera vez que configures el proyecto.

### 4. Ejecutar aplicación

```bash
streamlit run 🌿_Green_Scape.py
```

Abre http://localhost:8501

## 📊 Funcionalidades

| Página | Descripción |
|--------|-------------|
| **📊 Consultas Analíticas** | Productos, reacciones, likes, actividad de usuarios |
| **👤 Panel Usuario** | Perfil, historial, estadísticas personales |
| **💰 Gestor Precios** | Auditoría de cambios, triggers automáticos |
| **📄 Documentos Plantas** | Información jerárquica en MongoDB |
| **💬 Foro Comentarios** | Comentarios recursivos y threads |
| **⚔️ MySQL vs Mongo** | Comparativa de rendimiento  |

## 🛠️ Tecnologías

- **Frontend**: Streamlit
- **Backend**: Python 3.8 + ,mysql-connector, pymongo
- **Bases de Datos**: MySQL 8.0, MongoDB 7
- **DevOps**: Docker, Docker Compose

## 🐛 Solución de Problemas

**Verificar que el contenedor está corriendo**:
```bash
docker-compose ps
```

**Error de conexión MySQL:**
```bash
docker-compose restart
```

**Dependencias faltantes:**
```bash
pip install -r requirements.txt
```

**Puerto ocupado:**
```bash
docker-compose down
```

**Detener y eliminar los datos**:
```bash
docker-compose down -v
```
---

**Volver a iniciar**
```bash
docker-compose up -d
```