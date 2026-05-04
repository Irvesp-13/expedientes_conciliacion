# 🐳 Dockerización del Sistema de Conciliación

Este proyecto Django ahora está completamente dockerizado para facilitar su despliegue.

## 📋 Requisitos Previos

- Docker Desktop instalado
- Docker Compose instalado

## 🚀 Guía de Migración de Datos

### IMPORTANTE: Preservar tus datos existentes

Antes de levantar los contenedores por primera vez, necesitas exportar tus datos actuales de MySQL.

### Paso 1: Exportar datos actuales (BACKUP)

Desde tu MySQL local, ejecuta este comando en PowerShell:

```powershell
# Crear carpeta para backups si no existe
New-Item -ItemType Directory -Force -Path backups

# Exportar la base de datos actual
mysqldump -u root -p conciliacion > backups/conciliacion_backup.sql
```

Te pedirá la contraseña de root (en tu caso es `root`).

### Paso 2: Configurar variables de entorno

Copia el archivo de ejemplo y ajústalo si es necesario:

```powershell
Copy-Item .env.example .env
```

Puedes editar el archivo `.env` para cambiar contraseñas u otras configuraciones.

### Paso 3: Levantar los contenedores

```powershell
# Construir y levantar los contenedores
docker-compose up -d --build
```

Este comando:
- Construirá la imagen de Django
- Descargará MySQL 8.0
- Creará la red y volúmenes
- Levantará ambos contenedores

### Paso 4: Importar tus datos al contenedor MySQL

Espera unos 20-30 segundos a que MySQL inicie completamente, luego ejecuta:

```powershell
# Importar el backup a la base de datos en Docker
Get-Content backups/conciliacion_backup.sql | docker exec -i conciliacion_db mysql -u root -proot conciliacion
```

### Paso 5: Verificar que todo funciona

```powershell
# Ver los logs de los contenedores
docker-compose logs -f
```

Abre tu navegador en: http://localhost:8000

## 🔧 Comandos Útiles

### Ver contenedores en ejecución
```powershell
docker-compose ps
```

### Detener los contenedores
```powershell
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ BORRA DATOS)
```powershell
docker-compose down -v
```

### Ver logs
```powershell
# Todos los servicios
docker-compose logs -f

# Solo Django
docker-compose logs -f web

# Solo MySQL
docker-compose logs -f db
```

### Ejecutar comandos de Django
```powershell
# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Colectar archivos estáticos
docker-compose exec web python manage.py collectstatic
```

### Acceder a la base de datos MySQL
```powershell
docker-compose exec db mysql -u root -proot conciliacion
```

### Hacer backup de la base de datos en Docker
```powershell
docker-compose exec db mysqldump -u root -proot conciliacion > backups/conciliacion_docker_backup_$(Get-Date -Format "yyyy-MM-dd").sql
```

## 📦 Estructura de Archivos Docker

- **Dockerfile**: Define cómo se construye la imagen de Django
- **docker-compose.yml**: Orquesta los servicios (Django + MySQL)
- **.dockerignore**: Archivos excluidos de la imagen Docker
- **.env**: Variables de entorno (no se sube a Git)
- **.env.example**: Plantilla de variables de entorno
- **requirements.txt**: Dependencias de Python

## 🔒 Seguridad

1. **NO SUBAS** el archivo `.env` a Git (ya está en `.gitignore`)
2. Cambia el `SECRET_KEY` en producción
3. Cambia la contraseña de MySQL en producción
4. Configura `DEBUG=False` en producción

## 🌐 Despliegue en Servidor Interno

Para desplegar en un servidor:

1. Instala Docker y Docker Compose en el servidor
2. Copia todo el proyecto al servidor
3. Copia el archivo `.env` con las configuraciones adecuadas
4. Importa el backup de datos (Paso 4)
5. Ejecuta `docker-compose up -d`

### Actualizar ALLOWED_HOSTS

En tu archivo `.env` del servidor, actualiza:

```
ALLOWED_HOSTS=localhost,127.0.0.1,IP_DEL_SERVIDOR,DOMINIO_DEL_SERVIDOR
```

Por ejemplo:
```
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100,conciliacion.miempresa.local
```

## 🐛 Solución de Problemas

### El puerto 3306 ya está en uso
El `docker-compose.yml` usa el puerto 3307 en el host para evitar conflictos con MySQL local.

### Error de conexión a la base de datos
Espera unos segundos más a que MySQL inicie completamente. Verifica con:
```powershell
docker-compose logs db
```

### Los datos no se importaron
Verifica que el archivo de backup existe y vuelve a ejecutar el comando de importación del Paso 4.

### Cambios en el código no se reflejan
Reinicia el contenedor web:
```powershell
docker-compose restart web
```

## 📞 Soporte

Si tienes problemas, revisa los logs con `docker-compose logs -f` para identificar errores.
