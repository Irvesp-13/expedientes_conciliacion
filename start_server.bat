@echo off
cd /d C:\Sistemas\expedientes_conciliacion
call venv\Scripts\activate
waitress-serve --host=0.0.0.0 --port=8000 expedientes_conciliacion.wsgi:application
pause