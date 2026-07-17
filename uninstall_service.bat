@echo off
REM Elimina el servicio de Windows creado por install_service.bat
REM EJECUTAR COMO ADMINISTRADOR.
SET SERVICE_NAME=ExpedientesConciliacion
nssm stop %SERVICE_NAME%
nssm remove %SERVICE_NAME% confirm
echo Servicio %SERVICE_NAME% eliminado.
pause
