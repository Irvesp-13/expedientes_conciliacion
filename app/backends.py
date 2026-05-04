from django.contrib.auth.backends import BaseBackend
from .models import Empleado

class EmpleadoBackend(BaseBackend):
    def authenticate(self, request, clave_empleado=None):
        try:
            # Buscar al empleado por su clave de empleado
            empleado = Empleado.objects.get(clave_empleado=clave_empleado)
            return empleado  # Devuelve la instancia de Empleado
        except Empleado.DoesNotExist:
            return None  # Si no existe, devuelve None

    def get_user(self, user_id):
        try:
            return Empleado.objects.get(pk=user_id)
        except Empleado.DoesNotExist:
            return None