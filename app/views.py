from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import *
from .models import Empleado, Bitacora
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import CargaDescarga
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime


def registrar_accion(empleado, accion, descripcion, request=None):
    """
    Función auxiliar para registrar acciones en la bitácora
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    Bitacora.objects.create(
        empleado=empleado,
        accion=accion,
        descripcion=descripcion,
        ip_address=ip_address
    )


def iniciar_sesion(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        clave_empleado = request.POST['clave_empleado']
        
        try:
            # Buscar al empleado por su clave de empleado y nombre
            empleado = Empleado.objects.get(clave_empleado=clave_empleado, nombre=nombre)
            
            # Guardar el ID del empleado en la sesión
            request.session['empleado_id'] = empleado.id
            
            # Registrar en bitácora
            registrar_accion(empleado, 'Inicio de sesión', f'El usuario {empleado.nombre} inició sesión', request)
            
            return redirect('bienvenida')
        except Empleado.DoesNotExist:
            # Mostrar mensaje de error si las credenciales son incorrectas
            return render(request, 'iniciar_sesion.html', {'error': 'Credenciales incorrectas'})
    
    return render(request, 'iniciar_sesion.html')

def bienvenida(request):
    # Verificar si el empleado está autenticado
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    # Obtener el empleado autenticado
    empleado = Empleado.objects.get(id=empleado_id)
    
    # Obtener registros de la tabla expedientes
    expedientes = ConciliacionExpedientes.objects.all()
    
    return render(request, 'bienvenida.html', {
        'empleado': empleado,
        'expedientes': expedientes,
    })


def cerrar_sesion(request):
    # Registrar en bitácora antes de cerrar sesión
    empleado_id = request.session.get('empleado_id')
    if empleado_id:
        try:
            empleado = Empleado.objects.get(id=empleado_id)
            registrar_accion(empleado, 'Cierre de sesión', f'El usuario {empleado.nombre} cerró sesión', request)
        except Empleado.DoesNotExist:
            pass
    
    # Eliminar el ID del empleado de la sesión
    if 'empleado_id' in request.session:
        del request.session['empleado_id']
    return redirect('iniciar_sesion')

def agregar_expediente(request):
    # Verificar si el usuario está autenticado
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    
    if request.method == 'POST':
        # Get the last id_expediente and increment it
        last_expediente = ConciliacionExpedientes.objects.order_by('-id').first()
        new_id = 1 if not last_expediente else last_expediente.id + 1
        
        # Helper function to convert checkbox values
        def get_int_value(field_name):
            value = request.POST.get(field_name)
            return 1 if value == '1' or value == 'on' else None
        
        nuevo_expediente = ConciliacionExpedientes(
            id=new_id,
            letra=request.POST.get('letra', None),
            exp=request.POST.get('exp', None),
            anio=request.POST.get('anio', None),
            actor=request.POST.get('actor', None),
            demandado=request.POST.get('demandado', None),
            area_en_la_que_se_encuentra=request.POST.get('area_en_la_que_se_encuentra', None),
            acuerdo_pendiente_de_caducidad=get_int_value('acuerdo_pendiente_de_caducidad'),
            caducidad=get_int_value('caducidad'),
            acuerdo_pendiente_prescripcion=get_int_value('acuerdo_pendiente_prescripcion'),
            prescripcion=get_int_value('prescripcion'),
            convenio_en_tramite=get_int_value('convenio_en_tramite'),
            desistimiento=get_int_value('desistimiento'),
            por_no_interpuesta=get_int_value('por_no_interpuesta'),
            convenio_cumplimiento_laudo=get_int_value('convenio_cumplimiento_laudo'),
            archivado_por_recision=get_int_value('archivado_por_recision'),
            descentralizado=get_int_value('descentralizado'),
            incompetencia=get_int_value('incompetencia'),
            emplazamiento=get_int_value('emplazamiento'),
            falta_not_actor_emplazamiento=get_int_value('falta_not_actor_emplazamiento'),
            falta_emplazar=get_int_value('falta_emplazar'),
            no_han_senalado=get_int_value('no_han_senalado'),
            terminio=get_int_value('terminio'),
            imposibilidad_emplazamiento=get_int_value('imposibilidad_emplazamiento'),
            exhorto=get_int_value('exhorto'),
            procedimiento=get_int_value('procedimiento'),
            cita_conciliacion=get_int_value('cita_conciliacion'),
            sin_cita_conciliacion=get_int_value('sin_cita_conciliacion'),
            convenio_p_cumpl=get_int_value('convenio_p_cumpl'),
            cde=get_int_value('cde'),
            tercero_audiencia=get_int_value('tercero_audiencia'),
            oap=get_int_value('oap'),
            pruebas=get_int_value('pruebas'),
            reserva=get_int_value('reserva'),
            pendiente_revision=get_int_value('pendiente_revision'),
            notificadas_ambas=get_int_value('notificadas_ambas'),
            desahogo_pruebas=get_int_value('desahogo_pruebas'),
            falta_citar_test=get_int_value('falta_citar_test'),
            fata_not_partes=get_int_value('fata_not_partes'),
            fuerza_publica_testimonial=get_int_value('fuerza_publica_testimonial'),
            justificante=get_int_value('justificante'),
            actora=get_int_value('actora'),
            demandada=get_int_value('demandada'),
            tercero=get_int_value('tercero'),
            falta_designar_per=get_int_value('falta_designar_per'),
            falta_not_partes_conf=get_int_value('falta_not_partes_conf'),
            falta_ir_domicilio=get_int_value('falta_ir_domicilio'),
            f_hacer_oficio=get_int_value('f_hacer_oficio'),
            falta_girar_oficio=get_int_value('falta_girar_oficio'),
            sin_respuesta=get_int_value('sin_respuesta'),
            falta_inspeccion=get_int_value('falta_inspeccion'),
            falta_cotejo=get_int_value('falta_cotejo'),
            inc_nul_not=get_int_value('inc_nul_not'),
            cierre=get_int_value('cierre'),
            alegatos=get_int_value('alegatos'),
            prueba_pendiente=get_int_value('prueba_pendiente'),
            cierre_cierre=get_int_value('cierre_cierre'),
            pendiente_de_laudo=get_int_value('pendiente_de_laudo'),
            dictado=get_int_value('dictado'),
            falta_not_partes_dictados=get_int_value('falta_not_partes_dictados'),
            condenatorio=get_int_value('condenatorio'),
            absolutorio=get_int_value('absolutorio'),
            en_colegiado=get_int_value('en_colegiado'),
            ejecucion=get_int_value('ejecucion'),
            auto_ejecucion=get_int_value('auto_ejecucion'),
            falta_not_actor_ejecucion=get_int_value('falta_not_actor_ejecucion'),
            requerimiento=get_int_value('requerimiento'),
            fuerza_publica_requerimiento=get_int_value('fuerza_publica_requerimiento'),
            imposibilidad_requerimiento=get_int_value('imposibilidad_requerimiento'),
            inembargable=get_int_value('inembargable'),
            cuentas_embargadas=get_int_value('cuentas_embargadas'),
            embargo_de_bien_inmueble_yo_muebles=get_int_value('embargo_de_bien_inmueble_yo_muebles'),
            revision=get_int_value('revision'),
            falta_reso_rev=get_int_value('falta_reso_rev'),
            falta_not_partes_requerimiento=get_int_value('falta_not_partes_requerimiento'),
            remate=get_int_value('remate'),
            indirecto=get_int_value('indirecto'),
            emplazar=get_int_value('emplazar'),
            desahogo_pruebas_indirecto=get_int_value('desahogo_pruebas_indirecto'),
            dictar_laudo=get_int_value('dictar_laudo'),
            ejecucion_indirecto=get_int_value('ejecucion_indirecto'),
            directo=get_int_value('directo')
        )
        nuevo_expediente.save()
        
        # Registrar en bitácora
        registrar_accion(empleado, 'Crear expediente', f'Creó el expediente {request.POST.get("exp", "")} - Actor: {request.POST.get("actor", "")} vs Demandado: {request.POST.get("demandado", "")}', request)
        
        messages.success(request, 'Expediente agregado correctamente.')
        return redirect('bienvenida')
    
    return render(request, 'agregar_expediente.html')


def crear_empleado(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('bienvenida')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        clave_empleado = request.POST.get('clave_empleado')
        puesto = request.POST.get('puesto')
        if nombre and clave_empleado and puesto:
            if Empleado.objects.filter(clave_empleado=clave_empleado).exists():
                messages.error(request, 'La clave de empleado ya existe.')
            else:
                nuevo_empleado = Empleado.objects.create(
                    nombre=nombre,
                    clave_empleado=clave_empleado,
                    puesto=puesto
                )
                
                # Registrar en bitácora
                tipo_puesto = 'Administrador' if int(puesto) == 1 else 'Usuario normal'
                registrar_accion(empleado, 'Crear empleado', f'Creó el empleado {nombre} (Clave: {clave_empleado}) como {tipo_puesto}', request)
                
                messages.success(request, 'Empleado creado exitosamente.')
                return redirect('crear_empleado')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    empleados = Empleado.objects.all()
    return render(request, 'crear_empleado.html', {'empleados': empleados})

def ver_expediente(request, id_expediente):
    if not request.session.get('empleado_id'):
        return redirect('iniciar_sesion')
    
    try:
        expediente = ConciliacionExpedientes.objects.get(pk=id_expediente)
        return render(request, 'ver_expediente.html', {'expediente': expediente})
    except ConciliacionExpedientes.DoesNotExist:
        messages.error(request, 'El expediente no existe.')
        return redirect('bienvenida')

def editar_expediente(request, id_expediente):
    if not request.session.get('empleado_id'):
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=request.session['empleado_id'])
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('bienvenida')

    try:
        expediente = get_object_or_404(ConciliacionExpedientes, pk=id_expediente)
        
        if request.method == 'POST':
            # Helper function to convert checkbox values
            def get_int_value(field_name):
                value = request.POST.get(field_name)
                return 1 if value == '1' or value == 'on' else None
            
            # Update all fields
            expediente.letra = request.POST.get('letra', None)
            expediente.exp = request.POST.get('exp', None)
            expediente.anio = request.POST.get('anio', None)
            expediente.actor = request.POST.get('actor', None)
            expediente.demandado = request.POST.get('demandado', None)
            expediente.area_en_la_que_se_encuentra = request.POST.get('area_en_la_que_se_encuentra', None)
            expediente.acuerdo_pendiente_de_caducidad = get_int_value('acuerdo_pendiente_de_caducidad')
            expediente.caducidad = get_int_value('caducidad')
            expediente.acuerdo_pendiente_prescripcion = get_int_value('acuerdo_pendiente_prescripcion')
            expediente.prescripcion = get_int_value('prescripcion')
            expediente.convenio_en_tramite = get_int_value('convenio_en_tramite')
            expediente.desistimiento = get_int_value('desistimiento')
            expediente.por_no_interpuesta = get_int_value('por_no_interpuesta')
            expediente.convenio_cumplimiento_laudo = get_int_value('convenio_cumplimiento_laudo')
            expediente.archivado_por_recision = get_int_value('archivado_por_recision')
            expediente.descentralizado = get_int_value('descentralizado')
            expediente.incompetencia = get_int_value('incompetencia')
            expediente.emplazamiento = get_int_value('emplazamiento')
            expediente.falta_not_actor_emplazamiento = get_int_value('falta_not_actor_emplazamiento')
            expediente.falta_emplazar = get_int_value('falta_emplazar')
            expediente.no_han_senalado = get_int_value('no_han_senalado')
            expediente.terminio = get_int_value('terminio')
            expediente.imposibilidad_emplazamiento = get_int_value('imposibilidad_emplazamiento')
            expediente.exhorto = get_int_value('exhorto')
            expediente.procedimiento = get_int_value('procedimiento')
            expediente.cita_conciliacion = get_int_value('cita_conciliacion')
            expediente.sin_cita_conciliacion = get_int_value('sin_cita_conciliacion')
            expediente.convenio_p_cumpl = get_int_value('convenio_p_cumpl')
            expediente.cde = get_int_value('cde')
            expediente.tercero_audiencia = get_int_value('tercero_audiencia')
            expediente.oap = get_int_value('oap')
            expediente.pruebas = get_int_value('pruebas')
            expediente.reserva = get_int_value('reserva')
            expediente.pendiente_revision = get_int_value('pendiente_revision')
            expediente.notificadas_ambas = get_int_value('notificadas_ambas')
            expediente.desahogo_pruebas = get_int_value('desahogo_pruebas')
            expediente.falta_citar_test = get_int_value('falta_citar_test')
            expediente.fata_not_partes = get_int_value('fata_not_partes')
            expediente.fuerza_publica_testimonial = get_int_value('fuerza_publica_testimonial')
            expediente.justificante = get_int_value('justificante')
            expediente.actora = get_int_value('actora')
            expediente.demandada = get_int_value('demandada')
            expediente.tercero = get_int_value('tercero')
            expediente.falta_designar_per = get_int_value('falta_designar_per')
            expediente.falta_not_partes_conf = get_int_value('falta_not_partes_conf')
            expediente.falta_ir_domicilio = get_int_value('falta_ir_domicilio')
            expediente.f_hacer_oficio = get_int_value('f_hacer_oficio')
            expediente.falta_girar_oficio = get_int_value('falta_girar_oficio')
            expediente.sin_respuesta = get_int_value('sin_respuesta')
            expediente.falta_inspeccion = get_int_value('falta_inspeccion')
            expediente.falta_cotejo = get_int_value('falta_cotejo')
            expediente.inc_nul_not = get_int_value('inc_nul_not')
            expediente.cierre = get_int_value('cierre')
            expediente.alegatos = get_int_value('alegatos')
            expediente.prueba_pendiente = get_int_value('prueba_pendiente')
            expediente.cierre_cierre = get_int_value('cierre_cierre')
            expediente.pendiente_de_laudo = get_int_value('pendiente_de_laudo')
            expediente.dictado = get_int_value('dictado')
            expediente.falta_not_partes_dictados = get_int_value('falta_not_partes_dictados')
            expediente.condenatorio = get_int_value('condenatorio')
            expediente.absolutorio = get_int_value('absolutorio')
            expediente.en_colegiado = get_int_value('en_colegiado')
            expediente.ejecucion = get_int_value('ejecucion')
            expediente.auto_ejecucion = get_int_value('auto_ejecucion')
            expediente.falta_not_actor_ejecucion = get_int_value('falta_not_actor_ejecucion')
            expediente.requerimiento = get_int_value('requerimiento')
            expediente.fuerza_publica_requerimiento = get_int_value('fuerza_publica_requerimiento')
            expediente.imposibilidad_requerimiento = get_int_value('imposibilidad_requerimiento')
            expediente.inembargable = get_int_value('inembargable')
            expediente.cuentas_embargadas = get_int_value('cuentas_embargadas')
            expediente.embargo_de_bien_inmueble_yo_muebles = get_int_value('embargo_de_bien_inmueble_yo_muebles')
            expediente.revision = get_int_value('revision')
            expediente.falta_reso_rev = get_int_value('falta_reso_rev')
            expediente.falta_not_partes_requerimiento = get_int_value('falta_not_partes_requerimiento')
            expediente.remate = get_int_value('remate')
            expediente.indirecto = get_int_value('indirecto')
            expediente.emplazar = get_int_value('emplazar')
            expediente.desahogo_pruebas_indirecto = get_int_value('desahogo_pruebas_indirecto')
            expediente.dictar_laudo = get_int_value('dictar_laudo')
            expediente.ejecucion_indirecto = get_int_value('ejecucion_indirecto')
            expediente.directo = get_int_value('directo')
            
            expediente.save()
            
            # Registrar en bitácora
            registrar_accion(empleado, 'Editar expediente', f'Editó el expediente {expediente.letra} {expediente.exp}/{expediente.anio} - Actor: {expediente.actor} vs Demandado: {expediente.demandado}', request)
            
            messages.success(request, 'Expediente actualizado correctamente.')
            return redirect('bienvenida')
        
        return render(request, 'editar_expediente.html', {'expediente': expediente})
        
    except ConciliacionExpedientes.DoesNotExist:
        messages.error(request, 'El expediente no existe.')
        return redirect('bienvenida')


def crear_empleado(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('bienvenida')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        clave_empleado = request.POST.get('clave_empleado')
        puesto = request.POST.get('puesto')
        if nombre and clave_empleado and puesto:
            if Empleado.objects.filter(clave_empleado=clave_empleado).exists():
                messages.error(request, 'La clave de empleado ya existe.')
            else:
                nuevo_empleado = Empleado.objects.create(
                    nombre=nombre,
                    clave_empleado=clave_empleado,
                    puesto=puesto
                )
                
                # Registrar en bitácora
                tipo_puesto = 'Administrador' if int(puesto) == 1 else 'Usuario normal'
                registrar_accion(empleado, 'Crear empleado', f'Creó el empleado {nombre} (Clave: {clave_empleado}) como {tipo_puesto}', request)
                
                messages.success(request, 'Empleado creado exitosamente.')
                return redirect('crear_empleado')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    empleados = Empleado.objects.all()
    return render(request, 'crear_empleado.html', {'empleados': empleados})


def eliminar_expediente(request, id_expediente):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para eliminar expedientes.')
        return redirect('bienvenida')
    
    try:
        expediente = ConciliacionExpedientes.objects.get(pk=id_expediente)
        expediente.delete()
        messages.success(request, 'Expediente eliminado correctamente.')
    except ConciliacionExpedientes.DoesNotExist:
        messages.error(request, 'El expediente no existe.')
    
    return redirect('bienvenida')


def editar_empleado(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    admin = Empleado.objects.get(id=empleado_id)
    if not admin.es_administrador():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('bienvenida')

    empleado_edit = Empleado.objects.get(id=id)
    if request.method == 'POST':
        empleado_edit.nombre = request.POST.get('nombre')
        empleado_edit.clave_empleado = request.POST.get('clave_empleado')
        empleado_edit.puesto = request.POST.get('puesto')
        empleado_edit.save()
        
        # Registrar en bitácora
        tipo_puesto = 'Administrador' if int(empleado_edit.puesto) == 1 else 'Usuario normal'
        registrar_accion(admin, 'Editar empleado', f'Editó el empleado {empleado_edit.nombre} (Clave: {empleado_edit.clave_empleado}) - Puesto: {tipo_puesto}', request)
        
        messages.success(request, 'Empleado actualizado correctamente.')
        return redirect('crear_empleado')
    return render(request, 'editar_empleado.html', {'empleado': empleado_edit})

def eliminar_empleado(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    admin = Empleado.objects.get(id=empleado_id)
    if not admin.es_administrador():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('bienvenida')

    # Prevent self-deletion
    if int(id) == int(empleado_id):
        messages.error(request, 'No puedes eliminar tu propio usuario mientras estás conectado.')
        return redirect('crear_empleado')

    empleado_eliminar = Empleado.objects.get(id=id)
    nombre_eliminado = empleado_eliminar.nombre
    clave_eliminada = empleado_eliminar.clave_empleado
    
    empleado_eliminar.delete()
    
    # Registrar en bitácora
    registrar_accion(admin, 'Eliminar empleado', f'Eliminó el empleado {nombre_eliminado} (Clave: {clave_eliminada})', request)
    
    messages.success(request, 'Empleado eliminado correctamente.')
    return redirect('crear_empleado')


def cargar_expediente(request):
    if request.method == 'POST':
        empleado_id = request.session.get('empleado_id')
        expediente_id = request.POST.get('expediente_id')
        nombre_carga = request.POST.get('nombre_carga')

        try:
            empleado = Empleado.objects.get(id=empleado_id)
            expediente = ConciliacionExpedientes.objects.get(pk=expediente_id)
            
            carga = CargaDescarga(
                empleado=empleado,
                expediente=expediente,
                nombre_carga=nombre_carga
            )
            carga.save()
            
            # Registrar en bitácora
            registrar_accion(empleado, 'Cargar expediente', f'Cargó el expediente {expediente.letra} {expediente.exp}/{expediente.anio} - {nombre_carga}', request)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def ver_cargas(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    
    cargas = CargaDescarga.objects.all().order_by('-fecha')
    return render(request, 'ver_cargas.html', {'cargas': cargas})


# Remove @login_required decorator and keep the function as is
def archivar_expediente(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return JsonResponse({'success': False, 'error': 'Sesión no iniciada'})
    
    empleado = Empleado.objects.get(id=empleado_id)

    if request.method == 'POST':
        try:
            expedientes_ids = request.POST.getlist('expedientes_ids[]')
            motivo = request.POST.get('motivo')
            
            if not expedientes_ids:
                return JsonResponse({'success': False, 'error': 'No se seleccionaron expedientes'})
            
            archivados_count = 0
            for expediente_id in expedientes_ids:
                try:
                    expediente = ConciliacionExpedientes.objects.get(pk=expediente_id)
                    
                    # Create archive record with all fields as strings
                    Archivados.objects.create(
                        expediente=f"{expediente.letra or ''} {expediente.exp or ''}/{expediente.anio or ''}".strip(),
                        junta=expediente.area_en_la_que_se_encuentra,
                        actor=expediente.actor,
                        demandado=expediente.demandado,
                        motivo=motivo,
                        fecha_archivo=timezone.now()
                    )
                    
                    # Delete from original table
                    expediente.delete()
                    archivados_count += 1
                except ConciliacionExpedientes.DoesNotExist:
                    continue
            
            # Registrar en bitácora
            registrar_accion(empleado, 'Archivar expedientes', f'Archivó {archivados_count} expediente(s) - Motivo: {motivo}', request)
            
            return JsonResponse({
                'success': True, 
                'message': f'Se archivaron {archivados_count} expedientes correctamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def obtener_expedientes_ajax(request):
    """Vista para obtener expedientes mediante AJAX para el modal de archivado"""
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return JsonResponse({'success': False, 'error': 'Sesión no iniciada'})
    
    empleado = Empleado.objects.get(id=empleado_id)
    
    expedientes = ConciliacionExpedientes.objects.all()
    expedientes_list = [
        {
            'id': expediente.id,
            'expediente': f"{expediente.letra or ''} {expediente.exp or ''}/{expediente.anio or ''}".strip(),
            'junta': expediente.area_en_la_que_se_encuentra,
            'actor_nombre': expediente.actor,
            'demandado_nombre': expediente.demandado,
        }
        for expediente in expedientes
    ]
    
    return JsonResponse({'success': True, 'expedientes': expedientes_list})

# Remove @login_required decorator and keep the function as is
def ver_archivados(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    
    archivados = Archivados.objects.all().order_by('-fecha_archivo')
    return render(request, 'ver_archivados.html', {'archivados': archivados, 'empleado': empleado})

def exportar_expedientes_excel(request):
    # Verificar sesión
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        messages.error(request, 'Debes iniciar sesión')
        return redirect('iniciar_sesion')
    
    # Obtener todos los expedientes de la tabla 'expedientes'
    expedientes = ConciliacionExpedientes.objects.all()
    
    # Crear el libro de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Expedientes"
    
    # Estilos para el encabezado
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    # Definir las columnas según el modelo ConciliacionExpedientes actual
    headers = [
        'LETRA', 'EXPEDIENTE', 'AÑO', 'ACTOR', 'DEMANDADO', 'JUNTA/ÁREA',
        'ACU.PTE.CADUCIDAD', 'CADUCIDAD', 'ACU.PTE.PRESCRIPCIÓN', 'PRESCRIPCIÓN', 
        'CONVENIO EN TRÁMITE', 'DESISTIMIENTO', 'POR NO INTERPUESTA', 'CONVENIO CUMPL.LAUDO',
        'ARCHIVADO POR RESCISIÓN', 'DESCENTRALIZADO', 'INCOMPETENCIA',
        'EMPLAZAMIENTO', 'FALTA NOT.ACTOR EMPL', 'FALTA EMPLAZAR', 'NO HAN SEÑALADO',
        'TERMINIO', 'IMPOSIBILIDAD EMPL', 'EXHORTO',
        'PROCEDIMIENTO', 'CITA CONCILIACIÓN', 'SIN CITA CONCIL', 'CONVENIO P.CUMPL',
        'CDE', 'TERCERO AUDIENCIA', 'OAP',
        'PRUEBAS', 'RESERVA', 'PENDIENTE REVISIÓN', 'NOTIFICADAS AMBAS',
        'DESAHOGO PRUEBAS',
        'FALTA CITAR TEST', 'FALTA NOT.PARTES', 'FUERZA PÚBLICA TEST', 'JUSTIFICANTE',
        'ACTORA', 'DEMANDADA', 'TERCERO', 'FALTA DESIGNAR PER',
        'FALTA NOT.PARTES CONF', 'FALTA IR DOMICILIO',
        'FALTA HACER OFICIO', 'FALTA GIRAR OFICIO', 'SIN RESPUESTA',
        'FALTA INSPECCIÓN', 'FALTA COTEJO', 'INC.NUL.NOT',
        'CIERRE', 'ALEGATOS', 'PRUEBA PENDIENTE', 'CIERRE/DEPURACIÓN', 'PENDIENTE LAUDO',
        'DICTADO', 'FALTA NOT.PARTES DICT', 'CONDENATORIO', 'ABSOLUTORIO', 'EN COLEGIADO',
        'EJECUCIÓN', 'AUTO EJECUCIÓN', 'FALTA NOT.ACTOR EJEC',
        'REQUERIMIENTO', 'FUERZA PÚBLICA REQ', 'IMPOSIBILIDAD REQ', 'INEMBARGABLE',
        'CUENTAS EMBARGADAS', 'EMBARGO DE BIENES', 'REVISIÓN', 'FALTA RESO.REV',
        'FALTA NOT.PARTES REQ', 'REMATE',
        'AMPARO INDIRECTO', 'EMPLAZAR', 'DESAHOGO PRUEBAS IND', 'DICTAR LAUDO', 'EJECUCIÓN IND',
        'AMPARO DIRECTO'
    ]
    
    # Escribir encabezados
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        ws.column_dimensions[cell.column_letter].width = 12
    
    # Escribir los datos de los expedientes (mapeo de campos del modelo)
    column_fields = [
        'letra', 'exp', 'anio', 'actor', 'demandado', 'area_en_la_que_se_encuentra',
        'acuerdo_pendiente_de_caducidad', 'caducidad', 'acuerdo_pendiente_prescripcion',
        'prescripcion', 'convenio_en_tramite', 'desistimiento', 'por_no_interpuesta',
        'convenio_cumplimiento_laudo', 'archivado_por_recision', 'descentralizado',
        'incompetencia', 'emplazamiento', 'falta_not_actor_emplazamiento', 'falta_emplazar',
        'no_han_senalado', 'terminio', 'imposibilidad_emplazamiento', 'exhorto',
        'procedimiento', 'cita_conciliacion', 'sin_cita_conciliacion', 'convenio_p_cumpl',
        'cde', 'tercero_audiencia', 'oap', 'pruebas', 'reserva', 'pendiente_revision',
        'notificadas_ambas', 'desahogo_pruebas', 'falta_citar_test', 'fata_not_partes',
        'fuerza_publica_testimonial', 'justificante', 'actora', 'demandada', 'tercero',
        'falta_designar_per', 'falta_not_partes_conf', 'falta_ir_domicilio', 'f_hacer_oficio',
        'falta_girar_oficio', 'sin_respuesta', 'falta_inspeccion', 'falta_cotejo',
        'inc_nul_not', 'cierre', 'alegatos', 'prueba_pendiente', 'cierre_cierre',
        'pendiente_de_laudo', 'dictado', 'falta_not_partes_dictados', 'condenatorio',
        'absolutorio', 'en_colegiado', 'ejecucion', 'auto_ejecucion',
        'falta_not_actor_ejecucion', 'requerimiento', 'fuerza_publica_requerimiento',
        'imposibilidad_requerimiento', 'inembargable', 'cuentas_embargadas',
        'embargo_de_bien_inmueble_yo_muebles', 'revision', 'falta_reso_rev',
        'falta_not_partes_requerimiento', 'remate', 'indirecto', 'emplazar',
        'desahogo_pruebas_indirecto', 'dictar_laudo', 'ejecucion_indirecto', 'directo'
    ]
    
    for row_num, exp in enumerate(expedientes, 2):
        for col_num, field in enumerate(column_fields, 1):
            value = getattr(exp, field, None) or ''
            ws.cell(row=row_num, column=col_num).value = value
    
    # Preparar la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename=expedientes_{fecha_actual}.xlsx'
    
    # Guardar el libro en la respuesta
    wb.save(response)
    
    return response


def ver_bitacora(request):
    """Vista para mostrar la bitácora de acciones - solo para administradores"""
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permisos para ver la bitácora.')
        return redirect('bienvenida')
    
    # Obtener parámetros de filtro
    filtro_empleado = request.GET.get('empleado', '')
    filtro_accion = request.GET.get('accion', '')
    filtro_fecha = request.GET.get('fecha', '')
    
    # Construir query
    bitacora = Bitacora.objects.all()
    
    if filtro_empleado:
        bitacora = bitacora.filter(empleado__nombre__icontains=filtro_empleado)
    
    if filtro_accion:
        bitacora = bitacora.filter(accion__icontains=filtro_accion)
    
    if filtro_fecha:
        bitacora = bitacora.filter(fecha_hora__date=filtro_fecha)
    
    bitacora = bitacora.order_by('-fecha_hora')[:200]  # Limitar a 200 registros recientes
    
    return render(request, 'ver_bitacora.html', {
        'bitacora': bitacora,
        'empleado': empleado,
        'filtro_empleado': filtro_empleado,
        'filtro_accion': filtro_accion,
        'filtro_fecha': filtro_fecha
    })


def restaurar_expediente(request):
    """Vista para restaurar un expediente archivado"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return JsonResponse({'success': False, 'error': 'Sesión no iniciada'})
    
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        id_archivo = request.POST.get('id_archivo')
        
        if not id_archivo:
            return JsonResponse({'success': False, 'error': 'ID de archivo no proporcionado'})
        
        # Obtener el expediente archivado
        archivo = Archivados.objects.get(id_archivo=id_archivo)
        
        # Obtener el último id para generar uno nuevo
        last_expediente = ConciliacionExpedientes.objects.order_by('-id').first()
        new_id = 1 if not last_expediente else last_expediente.id + 1
        
        # Restaurar el expediente con los datos del archivo
        # Parseando expediente en formato "LETRA EXP/ANIO"
        try:
            partes = archivo.expediente.strip().split('/')
            if len(partes) == 2:
                anio_str = partes[1]
                exp_y_letra = partes[0].strip().split()
                if len(exp_y_letra) >= 2:
                    letra = exp_y_letra[0]
                    exp = '/'.join(exp_y_letra[1:])
                    anio = int(anio_str) if anio_str.isdigit() else None
                else:
                    letra = None
                    exp = partes[0]
                    anio = int(anio_str) if anio_str.isdigit() else None
            else:
                letra = None
                exp = archivo.expediente
                anio = None
        except:
            letra = None
            exp = archivo.expediente
            anio = None
        
        # Crear el expediente restaurado
        expediente_restaurado = ConciliacionExpedientes.objects.create(
            id=new_id,
            letra=letra,
            exp=exp,
            anio=anio,
            actor=archivo.actor,
            demandado=archivo.demandado,
            area_en_la_que_se_encuentra=archivo.junta,
        )
        
        # Registrar en bitácora
        registrar_accion(
            empleado, 
            'Restaurar expediente', 
            f'Restauró el expediente {archivo.expediente} - Actor: {archivo.actor} vs Demandado: {archivo.demandado}',
            request
        )
        
        # Eliminar el registro de archivados
        archivo.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Expediente {archivo.expediente} restaurado correctamente'
        })
        
    except Archivados.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Expediente archivado no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def eliminar_permanente(request):
    """Vista para eliminar permanentemente expedientes archivados - Solo administradores"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return JsonResponse({'success': False, 'error': 'Sesión no iniciada'})
    
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        
        # Verificar que sea administrador
        if not empleado.es_administrador():
            return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})
        
        import json
        archivos_ids = json.loads(request.POST.get('archivos_ids', '[]'))
        
        if not archivos_ids:
            return JsonResponse({'success': False, 'error': 'No se seleccionaron expedientes'})
        
        eliminados_count = 0
        expedientes_eliminados = []
        
        for id_archivo in archivos_ids:
            try:
                archivo = Archivados.objects.get(id_archivo=id_archivo)
                expedientes_eliminados.append(f"{archivo.expediente} - {archivo.actor} vs {archivo.demandado}")
                archivo.delete()
                eliminados_count += 1
            except Archivados.DoesNotExist:
                continue
        
        # Registrar en bitácora
        descripcion = f'Eliminó permanentemente {eliminados_count} expediente(s) archivado(s): {", ".join(expedientes_eliminados[:3])}'
        if len(expedientes_eliminados) > 3:
            descripcion += f' y {len(expedientes_eliminados) - 3} más'
        
        registrar_accion(empleado, 'Eliminar permanentemente', descripcion, request)
        
        return JsonResponse({
            'success': True,
            'message': f'Se eliminaron permanentemente {eliminados_count} expediente(s)'
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
