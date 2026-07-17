# Guía de Despliegue en Windows 10 (XAMPP + Waitress)

Esta guía explica cómo dejar corriendo el **Sistema de Expedientes de Conciliación**
en la computadora Windows 10 donde ya tienen XAMPP, como un servicio real de
producción (no `runserver`).

```
                Internet / Red local
                        |
                Apache de XAMPP :80  (proxy inverso, opcional)
                        |
                Waitress :8000  (aplicación Django)  <-- SOLO 127.0.0.1
                        |
                MySQL de XAMPP  (base de datos conciliacion)
```

---

## 0. Prerrequisitos en la PC servidor

- Windows 10 con **XAMPP** instalado (Apache + MySQL/MariaDB).
- **Python 3.11+** instalado y en el PATH.
- El código del proyecto en `C:\Sistemas\expedientes_conciliacion`
  (ruta usada por `start_server.bat` y `install_service.bat`).
- **NSSM** para crear el servicio de Windows: https://nssm.cc/download
  (poner `nssm.exe` en el PATH o junto a los `.bat`).

> Nota: si la carpeta del proyecto está en otra ruta, edite
> `PROJECT_DIR` en `install_service.bat` y `start_server.bat`.

---

## 1. Preparar la base de datos (MySQL de XAMPP)

1. Abrir el Panel de Control de XAMPP y arrancar **MySQL**.
2. Entrar a `http://localhost/phpmyadmin` (o consola mysql) y crear la BD:

   ```sql
   CREATE DATABASE conciliacion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. El usuario por defecto en `.env` es `root` / sin contraseña (XAMPP).
   Si pusieron contraseña a root, actualicen `DB_PASSWORD` en `.env`.

---

## 2. Instalar dependencias y preparar Django

Abrir **CMD como administrador** en la carpeta del proyecto:

```bat
cd C:\Sistemas\expedientes_conciliacion
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

`collectstatic` es obligatorio en producción (DEBUG=False) porque WhiteNoise
sirve los estáticos desde `staticfiles/`.

---

## 3. Verificar que arranca (prueba manual)

```bat
venv\Scripts\activate
python serve.py
```

Debe imprimir `Iniciando expedientes_conciliacion en http://0.0.0.0:8000`
y entre a `http://127.0.0.1:8000`. Para salir: `Ctrl+C`.

También pueden usar el `.bat` ya existente: `start_server.bat`.

---

## 4. Registrarlo como SERVICIO DE WINDOWS (arranque automático)

Ejecutar **como administrador** `install_service.bat`.

Esto usa NSSM para crear el servicio `ExpedientesConciliacion`, que:
- corre `venv\Scripts\python.exe serve.py`,
- arranca solo con Windows (SERVICE_AUTO_START),
- guarda logs en `C:\Sistemas\expedientes_conciliacion\logs\`.

Comandos útiles:
```bat
nssm start   ExpedientesConciliacion
nssm stop    ExpedientesConciliacion
nssm restart ExpedientesConciliacion
uninstall_service.bat   (para quitarlo)
```

---

## 5. (Recomendado) Exponer vía Apache de XAMPP

Para usar el puerto 80 y un nombre limpio/HTTPS, Apache hace de proxy inverso
hacia Waitress en `127.0.0.1:8000`.

1. En `C:\xampp\apache\conf\httpd.conf` habilitar (quitar el `#`):
   ```
   LoadModule proxy_module modules/mod_proxy.so
   LoadModule proxy_http_module modules/mod_proxy_http.so
   ```
2. Pegar al final el contenido de **`apache_proxy.conf`** (incluido en este repo),
   ajustando `ServerName` a la IP/dominio real si aplica.
3. Reiniciar Apache desde el Panel de XAMPP.
4. Entrar a `http://localhost` (Apache redirige al Django en :8000).

> Waitress queda en `127.0.0.1` (no expuesto directo) por seguridad;
> por eso `.env` usa `APP_HOST=127.0.0.1`.

---

## 6. Configuración de producción ya aplicada

El archivo `.env` ya viene ajustado para producción:
- `DEBUG=False`
- `SECRET_KEY` fuerte (generado, no el de desarrollo)
- `ALLOWED_HOSTS=localhost,127.0.0.1`  ->  **añadir aquí la IP/dominio real**
  del servidor si se accederá desde otra PC de la red.

---

## 7. Respaldos

La carpeta `backups/` ya existe en el repo. Recomendación: programar una tarea
de Windows (Task Scheduler) que corra un `mysqldump` de la BD `conciliacion`
hacia `backups/`, por ejemplo:

```bat
"C:\xampp\mysql\bin\mysqldump.exe" -u root conciliacion > backups\conciliacion_%date:~6,4%%date:~3,2%%date:~0,2%.sql
```

---

## Archivos nuevos incluidos para despliegue

| Archivo | Para qué sirve |
|---|---|
| `serve.py` | Arranque de producción con Waitress (hilos/timeouts). |
| `install_service.bat` | Registra la app como servicio de Windows con NSSM. |
| `uninstall_service.bat` | Quita el servicio de Windows. |
| `apache_proxy.conf` | Configuración de proxy inverso para Apache (XAMPP). |
| `.env` | Ajustado a producción (DEBUG=False, SECRET_KEY fuerte). |
