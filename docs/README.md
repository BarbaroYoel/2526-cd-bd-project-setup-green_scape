# Base de Datos GreenScape - MySQL Docker

Este proyecto contiene la configuración de Docker para crear y cargar automáticamente parte de la base de datos **GreenScape** en MySQL.

## 📁 Archivos

- `Dockerfile`: Define la imagen Docker basada en MySQL 8.0
- `docker-compose.yml`: Configuración de Docker Compose para facilitar el despliegue
- pliegue
- `init.sql`: Script SQL con todas las tablas y datos iniciales
- `guidelines.tex`: Orientación del proyecto

## 🚀 Uso a través de Docker Compose 

1. **Iniciar el contenedor**:
   ```bash
   docker-compose up -d
   ```

2. **Verificar que el contenedor está corriendo**:
   ```bash
   docker-compose ps
   ```

3. **Conectarse a MySQL**:
   ```bash
   docker exec -it greenscape_mysql mysql -u root -p
   # Contraseña: root
   ```

4. **Detener el contenedor**:
   ```bash
   docker-compose down
   ```

5. **Detener y eliminar los datos**:
   ```bash
   docker-compose down -v
   ```

## 🔐 Credenciales

- **Host**: localhost
- **Puerto**: 3306
- **Usuario root**: root / root
- **Usuario adicional**: greenscape_user / greenscape_pass
- **Base de datos**: GreenScape

## 🔌 Conectar desde Jupyter Notebook

Para conectarse desde un notebook Jupyter usando `ipython-sql`:

```python
%load_ext sql
%sql mysql://root:root@localhost:3306/GreenScape
```

O si estás usando el mismo docker-compose que el notebook:

```python
%load_ext sql
%sql mysql://root:root@mysqllab:3306/GreenScape
```

## 🛠️ Reiniciar la base de datos

Si necesitas reiniciar la base de datos con los datos iniciales:

```bash
# Detener y eliminar el contenedor y volumen
docker-compose down -v

# Volver a iniciar
docker-compose up -d
```


