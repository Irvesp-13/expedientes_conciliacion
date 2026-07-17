@echo off
REM ============================================================
REM  Instala expedientes_conciliacion como SERVICIO DE WINDOWS
REM  usando NSSM (Non-Sucking Service Manager).
REM
REM  Requisitos:
REM    - Tener nssm.exe en el PATH o junto a este archivo.
REM      Descargar desde: https://nssm.cc/download
REM    - Haber ejecutado ya: pip install -r requirements.txt
REM      y: python manage.py migrate / collectstatic
REM
REM  EJECUTAR ESTE ARCHIVO COMO ADMINISTRADOR.
REM ============================================================

SET PROJECT_DIR=C:\Sistemas\expedientes_conciliacion
SET SERVICE_NAME=ExpedientesConciliacion
SET VENV_PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe

echo ------------------------------------------
echo  Registrando servicio %SERVICE_NAME% ...
echo  Directorio: %PROJECT_DIR%
echo ------------------------------------------

nssm install %SERVICE_NAME% "%VENV_PYTHON%" "%PROJECT_DIR%\serve.py"
nssm set %SERVICE_NAME% AppDirectory "%PROJECT_DIR%"
nssm set %SERVICE_NAME% DisplayName "Sistema de Expedientes de Conciliacion"
nssm set %SERVICE_NAME% Description "Aplicacion Django servida con Waitress"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppStdout "%PROJECT_DIR%\logs\waitress.out.log"
nssm set %SERVICE_NAME% AppStderr "%PROJECT_DIR%\logs\waitress.err.log"
nssm set %SERVICE_NAME% AppRotateFiles 1
nssm set %SERVICE_NAME% AppRotateBytes 1048576

echo.
echo  Iniciando servicio ...
nssm start %SERVICE_NAME%

echo.
echo  Listo. El servicio arrancara solo con Windows.
echo  Para detener:  nssm stop  %SERVICE_NAME%
echo  Para eliminar: nssm remove %SERVICE_NAME% confirm
pause
