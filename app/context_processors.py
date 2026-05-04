from .models import Empleado

def empleado_actual(request):
    empleado_id = request.session.get('empleado_id')
    if empleado_id:
        empleado = Empleado.objects.get(id=empleado_id)
        return {'empleado': empleado}
    return {}