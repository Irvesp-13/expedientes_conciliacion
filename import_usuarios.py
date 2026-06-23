import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expedientes_conciliacion.settings')
django.setup()

from app.models import Empleado

csv_path = 'CargaUsuarios.csv'

with open(csv_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rol = int(row.get('rol') or 2)
        # Mapear puesto a rol si es necesario
        puesto_text = (row.get('puesto') or '').lower()
        if puesto_text in ('admin', 'administrador'):
            rol = 1
        elif puesto_text in ('presidente', 'secretaria general', 'desarrollador del sistema'):
            rol = 1
        
        empleado = Empleado(
            usuario=row.get('usuario') or '',
            nombre=row['nombre'],
            clave_empleado=row['clave_empleado'],
            rol=rol,
            id_plaza=row.get('id_plaza') or '',
            puesto=row.get('puesto') or '',
        )
        empleado.save()
        print(f"Importado: {empleado.nombre} (clave: {empleado.clave_empleado}, rol: {empleado.rol})")

print("Importación completada.")