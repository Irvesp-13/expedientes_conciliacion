from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from .models import *
from .models import Empleado, Bitacora, crear_tabla_expediente_periodo, obtener_periodos_disponibles, get_periodo_actual
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import CargaDescarga
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime
from urllib.parse import quote


def pagina_no_encontrada(request, exception=None):
    return render(request, '404.html', status=404)


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


def redirigir_a_error(mensaje):
    return redirect(f"{reverse('error')}?mensaje={quote(mensaje)}")


def error(request):
    mensajes = [str(message) for message in messages.get_messages(request)]
    mensaje = request.GET.get('mensaje') or (mensajes[0] if mensajes else 'No tienes permiso para acceder a esta página.')
    return render(request, 'error.html', {'mensaje': mensaje})


def formatear_identificador_expediente(expediente):
    partes = [expediente.letra, expediente.exp, str(expediente.anio) if expediente.anio is not None else None]
    identificador = ' '.join(parte for parte in partes if parte)
    return identificador or f'Expediente {expediente.pk}'


def obtener_snapshot_expediente(expediente):
    snapshot = {}
    for field in ConciliacionExpedientes._meta.fields:
        if field.name != 'id':
            snapshot[field.name] = getattr(expediente, field.name)
    return snapshot


def obtener_campos_exportables_expediente():
    etiquetas = {
        'letra': 'LETRA',
        'exp': 'EXPEDIENTE',
        'anio': 'AÑO',
        'actor': 'ACTOR',
        'demandado': 'DEMANDADO',
        'area_en_la_que_se_encuentra': 'JUNTA/ÁREA',
        'acuerdo_pendiente_de_caducidad': 'ACU.PTE.CADUCIDAD',
        'caducidad': 'CADUCIDAD',
        'acuerdo_pendiente_prescripcion': 'ACU.PTE.PRESCRIPCIÓN',
        'prescripcion': 'PRESCRIPCIÓN',
        'convenio_en_tramite': 'CONVENIO EN TRÁMITE',
        'desistimiento': 'DESISTIMIENTO',
        'por_no_interpuesta': 'POR NO INTERPUESTA',
        'convenio_cumplimiento_laudo': 'CONVENIO CUMPL.LAUDO',
        'archivado_por_recision': 'ARCHIVADO POR RESCISIÓN',
        'descentralizado': 'DESCENTRALIZADO',
        'incompetencia': 'INCOMPETENCIA',
        'emplazamiento': 'EMPLAZAMIENTO',
        'falta_not_actor_emplazamiento': 'FALTA NOT.ACTOR EMPL',
        'falta_emplazar': 'FALTA EMPLAZAR',
        'no_han_senalado': 'NO HAN SEÑALADO',
        'terminio': 'TERMINIO',
        'imposibilidad_emplazamiento': 'IMPOSIBILIDAD EMPL',
        'exhorto': 'EXHORTO',
        'procedimiento': 'PROCEDIMIENTO',
        'cita_conciliacion': 'CITA CONCILIACIÓN',
        'sin_cita_conciliacion': 'SIN CITA CONCIL',
        'convenio_p_cumpl': 'CONVENIO P.CUMPL',
        'cde': 'CDE',
        'tercero_audiencia': 'TERCERO AUDIENCIA',
        'oap': 'OAP',
        'pruebas': 'PRUEBAS',
        'reserva': 'RESERVA',
        'pendiente_revision': 'PENDIENTE REVISIÓN',
        'notificadas_ambas': 'NOTIFICADAS AMBAS',
        'desahogo_pruebas': 'DESAHOGO PRUEBAS',
        'falta_citar_test': 'FALTA CITAR TEST',
        'fata_not_partes': 'FALTA NOT.PARTES',
        'fuerza_publica_testimonial': 'FUERZA PÚBLICA TEST',
        'justificante': 'JUSTIFICANTE',
        'actora': 'ACTORA',
        'demandada': 'DEMANDADA',
        'tercero': 'TERCERO',
        'falta_designar_per': 'FALTA DESIGNAR PER',
        'falta_not_partes_conf': 'FALTA NOT.PARTES CONF',
        'falta_ir_domicilio': 'FALTA IR DOMICILIO',
        'f_hacer_oficio': 'FALTA HACER OFICIO',
        'falta_girar_oficio': 'FALTA GIRAR OFICIO',
        'sin_respuesta': 'SIN RESPUESTA',
        'falta_inspeccion': 'FALTA INSPECCIÓN',
        'falta_cotejo': 'FALTA COTEJO',
        'inc_nul_not': 'INC.NUL.NOT',
        'cierre': 'CIERRE',
        'alegatos': 'ALEGATOS',
        'prueba_pendiente': 'PRUEBA PENDIENTE',
        'cierre_cierre': 'CIERRE/DEPURACIÓN',
        'pendiente_de_laudo': 'PENDIENTE LAUDO',
        'dictado': 'DICTADO',
        'falta_not_partes_dictados': 'FALTA NOT.PARTES DICT',
        'condenatorio': 'CONDENATORIO',
        'absolutorio': 'ABSOLUTORIO',
        'en_colegiado': 'EN COLEGIADO',
        'ejecucion': 'EJECUCIÓN',
        'auto_ejecucion': 'AUTO EJECUCIÓN',
        'falta_not_actor_ejecucion': 'FALTA NOT.ACTOR EJEC',
        'requerimiento': 'REQUERIMIENTO',
        'fuerza_publica_requerimiento': 'FUERZA PÚBLICA REQ',
        'imposibilidad_requerimiento': 'IMPOSIBILIDAD REQ',
        'inembargable': 'INEMBARGABLE',
        'cuentas_embargadas': 'CUENTAS EMBARGADAS',
        'embargo_de_bien_inmueble_yo_muebles': 'EMBARGO DE BIENES',
        'revision': 'REVISIÓN',
        'falta_reso_rev': 'FALTA RESO.REV',
        'falta_not_partes_requerimiento': 'FALTA NOT.PARTES REQ',
        'remate': 'REMATE',
        'indirecto': 'AMPARO INDIRECTO',
        'emplazar': 'EMPLAZAR',
        'desahogo_pruebas_indirecto': 'DESAHOGO PRUEBAS IND',
        'dictar_laudo': 'DICTAR LAUDO',
        'ejecucion_indirecto': 'EJECUCIÓN IND',
        'directo': 'AMPARO DIRECTO',
    }

    campos = [field.name for field in ConciliacionExpedientes._meta.fields if field.name != 'id']
    return [(campo, etiquetas.get(campo, campo.replace('_', ' ').upper())) for campo in campos]


def obtener_etiqueta_puesto(puesto):
    if puesto:
        return str(puesto)
    return 'Sin puesto'


def obtener_etiqueta_rol(rol):
    try:
        return Empleado.Rol(int(rol)).label
    except (TypeError, ValueError):
        return 'Rol desconocido'


def iniciar_sesion(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '')
        clave_empleado = request.POST.get('clave_empleado', '')
        
        if not usuario or not clave_empleado:
            return render(request, 'iniciar_sesion.html', {'error': 'Por favor complete usuario y clave'})
        
        try:
            empleado = Empleado.objects.get(clave_empleado=clave_empleado, usuario=usuario)
            
            request.session['empleado_id'] = empleado.id
            
            registrar_accion(empleado, 'Inicio de sesión', f'El usuario {empleado.usuario} inició sesión', request)
            
            return redirect('bienvenida')
        except Empleado.DoesNotExist:
            return render(request, 'iniciar_sesion.html', {'error': 'Credenciales incorrectas'})
    
    return render(request, 'iniciar_sesion.html')

def bienvenida(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    
    periodo_seleccionado = request.GET.get('periodo') or 'enero_2026'
    request.session['periodo_actual'] = periodo_seleccionado
    
    # Asegurar que la tabla exista
    crear_tabla_expediente_periodo(periodo_seleccionado)
    
    # Obtener expedientes de la tabla del periodo usando SQL
    table_name = f"expediente_{periodo_seleccionado}"
    fields = [f.name for f in ConciliacionExpedientes._meta.fields]
    
    expedientes_list = []
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT {', '.join(fields)} FROM `{table_name}` ORDER BY id")
        for row in cursor.fetchall():
            expediente = ExpedienteDinamico(row, table_name)
            expedientes_list.append(expediente)
    
    # Paginado manual sobre la lista
    paginator = Paginator(expedientes_list, 100)
    page_number = request.GET.get('page') or '1'
    try:
        expedientes = paginator.page(page_number)
    except:
        expedientes = paginator.page(1)
    
    empleados_carga = Empleado.objects.exclude(pk=empleado.id).order_by('nombre')
    periodos_disponibles = obtener_periodos_disponibles()
    
    periodos_con_nombres = []
    for p in periodos_disponibles:
        partes = p.split('_')
        mes = partes[0].title() if len(partes) > 0 else ''
        año = partes[1] if len(partes) > 1 else ''
        periodos_con_nombres.append({'clave': p, 'nombre': f'{mes} {año}'})
    
    return render(request, 'bienvenida.html', {
        'empleado': empleado,
        'expedientes': expedientes,
        'empleados_carga': empleados_carga,
        'periodo_actual': periodo_seleccionado,
        'periodos_disponibles': periodos_con_nombres,
    })


class ExpedienteDinamico:
    def __init__(self, row, table_name):
        fields = [
            'id', 'letra', 'exp', 'anio', 'actor', 'demandado', 'area_en_la_que_se_encuentra',
            'acuerdo_pendiente_de_caducidad', 'caducidad', 'acuerdo_pendiente_prescripcion', 'prescripcion',
            'convenio_en_tramite', 'desistimiento', 'por_no_interpuesta', 'convenio_cumplimiento_laudo',
            'archivado_por_recision', 'descentralizado', 'incompetencia', 'emplazamiento',
            'falta_not_actor_emplazamiento', 'falta_emplazar', 'no_han_senalado', 'terminio',
            'imposibilidad_emplazamiento', 'exhorto', 'procedimiento', 'cita_conciliacion',
            'sin_cita_conciliacion', 'convenio_p_cumpl', 'cde', 'tercero_audiencia', 'oap',
            'pruebas', 'reserva', 'pendiente_revision', 'notificadas_ambas', 'desahogo_pruebas',
            'falta_citar_test', 'fata_not_partes', 'fuerza_publica_testimonial', 'justificante',
            'actora', 'demandada', 'tercero', 'falta_designar_per', 'falta_not_partes_conf',
            'falta_ir_domicilio', 'f_hacer_oficio', 'falta_girar_oficio', 'sin_respuesta',
            'falta_inspeccion', 'falta_cotejo', 'inc_nul_not', 'cierre', 'alegatos',
            'prueba_pendiente', 'cierre_cierre', 'pendiente_de_laudo', 'dictado',
            'falta_not_partes_dictados', 'condenatorio', 'absolutorio', 'en_colegiado',
            'ejecucion', 'auto_ejecucion', 'falta_not_actor_ejecucion', 'requerimiento',
            'fuerza_publica_requerimiento', 'imposibilidad_requerimiento', 'inembargable',
            'cuentas_embargadas', 'embargo_de_bien_inmueble_yo_muebles', 'revision', 'falta_reso_rev',
            'falta_not_partes_requerimiento', 'remate', 'indirecto', 'emplazar',
            'desahogo_pruebas_indirecto', 'dictar_laudo', 'ejecucion_indirecto', 'directo'
        ]
        for i, field in enumerate(fields):
            setattr(self, field, row[i] if i < len(row) else None)
        self._table_name = table_name
    
    def __str__(self):
        partes = [self.letra, self.exp, str(self.anio) if self.anio else None]
        return ' '.join(str(p) for p in partes if p) or f'Expediente {self.id}'


def crear_periodo(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirigir_a_error('No tienes permiso para acceder a esta página.')
    
    if request.method == 'POST':
        mes = request.POST.get('mes')
        anio = request.POST.get('anio')
        if mes and anio:
            periodo = f"{mes}_{anio}"
            crear_tabla_expediente_periodo(periodo)
            registrar_accion(empleado, 'Crear periodo', f'Creó el periodo {mes} {anio}', request)
            messages.success(request, f'Periodo {mes} {anio} creado correctamente.')
            return redirect(f"{reverse('bienvenida')}?periodo={periodo}")
        else:
            messages.error(request, 'Selecciona mes y año.')
    
    return render(request, 'crear_periodo.html', {
        'meses': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
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
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirigir_a_error('No tienes permiso para acceder a esta página.')
    
    # Obtener periodo del GET o sesión
    periodo_get = request.GET.get('periodo')
    if periodo_get:
        periodo_seleccionado = periodo_get
        request.session['periodo_actual'] = periodo_seleccionado
    else:
        periodo_seleccionado = request.session.get('periodo_actual') or 'enero_2026'
    
    if request.method == 'POST':
        # Asegurar que la tabla exista
        crear_tabla_expediente_periodo(periodo_seleccionado)
        table_name = f"expediente_{periodo_seleccionado}"
        
        # Obtener el último id de la tabla del periodo
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT MAX(id) FROM `{table_name}`")
            last_id = cursor.fetchone()[0]
            new_id = 1 if last_id is None else last_id + 1
        
        # Helper function to convert checkbox values
        def get_int_value(field_name):
            value = request.POST.get(field_name)
            return 1 if value == '1' or value == 'on' else None
        
        # Campos del expediente
        fields = ['id', 'letra', 'exp', 'anio', 'actor', 'demandado', 'area_en_la_que_se_encuentra',
                  'acuerdo_pendiente_de_caducidad', 'caducidad', 'acuerdo_pendiente_prescripcion', 'prescripcion',
                  'convenio_en_tramite', 'desistimiento', 'por_no_interpuesta', 'convenio_cumplimiento_laudo',
                  'archivado_por_recision', 'descentralizado', 'incompetencia', 'emplazamiento',
                  'falta_not_actor_emplazamiento', 'falta_emplazar', 'no_han_senalado', 'terminio',
                  'imposibilidad_emplazamiento', 'exhorto', 'procedimiento', 'cita_conciliacion',
                  'sin_cita_conciliacion', 'convenio_p_cumpl', 'cde', 'tercero_audiencia', 'oap',
                  'pruebas', 'reserva', 'pendiente_revision', 'notificadas_ambas', 'desahogo_pruebas',
                  'falta_citar_test', 'fata_not_partes', 'fuerza_publica_testimonial', 'justificante',
                  'actora', 'demandada', 'tercero', 'falta_designar_per', 'falta_not_partes_conf',
                  'falta_ir_domicilio', 'f_hacer_oficio', 'falta_girar_oficio', 'sin_respuesta',
                  'falta_inspeccion', 'falta_cotejo', 'inc_nul_not', 'cierre', 'alegatos',
                  'prueba_pendiente', 'cierre_cierre', 'pendiente_de_laudo', 'dictado',
                  'falta_not_partes_dictados', 'condenatorio', 'absolutorio', 'en_colegiado',
                  'ejecucion', 'auto_ejecucion', 'falta_not_actor_ejecucion', 'requerimiento',
                  'fuerza_publica_requerimiento', 'imposibilidad_requerimiento', 'inembargable',
                  'cuentas_embargadas', 'embargo_de_bien_inmueble_yo_muebles', 'revision', 'falta_reso_rev',
                  'falta_not_partes_requerimiento', 'remate', 'indirecto', 'emplazar',
                  'desahogo_pruebas_indirecto', 'dictar_laudo', 'ejecucion_indirecto', 'directo']
        
        values = [
            new_id, request.POST.get('letra', ''), request.POST.get('exp', ''), request.POST.get('anio') or None,
            request.POST.get('actor', ''), request.POST.get('demandado', ''), request.POST.get('area_en_la_que_se_encuentra', ''),
            get_int_value('acuerdo_pendiente_de_caducidad'), get_int_value('caducidad'), get_int_value('acuerdo_pendiente_prescripcion'),
            get_int_value('prescripcion'), get_int_value('convenio_en_tramite'), get_int_value('desistimiento'),
            get_int_value('por_no_interpuesta'), get_int_value('convenio_cumplimiento_laudo'), get_int_value('archivado_por_recision'),
            get_int_value('descentralizado'), get_int_value('incompetencia'), get_int_value('emplazamiento'),
            get_int_value('falta_not_actor_emplazamiento'), get_int_value('falta_emplazar'), get_int_value('no_han_senalado'),
            get_int_value('terminio'), get_int_value('imposibilidad_emplazamiento'), get_int_value('exhorto'),
            get_int_value('procedimiento'), get_int_value('cita_conciliacion'), get_int_value('sin_cita_conciliacion'),
            get_int_value('convenio_p_cumpl'), get_int_value('cde'), get_int_value('tercero_audiencia'),
            get_int_value('oap'), get_int_value('pruebas'), get_int_value('reserva'), get_int_value('pendiente_revision'),
            get_int_value('notificadas_ambas'), get_int_value('desahogo_pruebas'), get_int_value('falta_citar_test'),
            get_int_value('fata_not_partes'), get_int_value('fuerza_publica_testimonial'), get_int_value('justificante'),
            get_int_value('actora'), get_int_value('demandada'), get_int_value('tercero'),
            get_int_value('falta_designar_per'), get_int_value('falta_not_partes_conf'), get_int_value('falta_ir_domicilio'),
            get_int_value('f_hacer_oficio'), get_int_value('falta_girar_oficio'), get_int_value('sin_respuesta'),
            get_int_value('falta_inspeccion'), get_int_value('falta_cotejo'), get_int_value('inc_nul_not'),
            get_int_value('cierre'), get_int_value('alegatos'), get_int_value('prueba_pendiente'),
            get_int_value('cierre_cierre'), get_int_value('pendiente_de_laudo'), get_int_value('dictado'),
            get_int_value('falta_not_partes_dictados'), get_int_value('condenatorio'), get_int_value('absolutorio'),
            get_int_value('en_colegiado'), get_int_value('ejecucion'), get_int_value('auto_ejecucion'),
            get_int_value('falta_not_actor_ejecucion'), get_int_value('requerimiento'),
            get_int_value('fuerza_publica_requerimiento'), get_int_value('imposibilidad_requerimiento'),
            get_int_value('inembargable'), get_int_value('cuentas_embargadas'),
            get_int_value('embargo_de_bien_inmueble_yo_muebles'), get_int_value('revision'),
            get_int_value('falta_reso_rev'), get_int_value('falta_not_partes_requerimiento'),
            get_int_value('remate'), get_int_value('indirecto'), get_int_value('emplazar'),
            get_int_value('desahogo_pruebas_indirecto'), get_int_value('dictar_laudo'),
            get_int_value('ejecucion_indirecto'), get_int_value('directo')
        ]
        
        placeholders = ', '.join(['%s'] * len(fields))
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO `{table_name}` ({', '.join(fields)}) VALUES ({placeholders})", 
                values
            )
        
        registrar_accion(empleado, 'Crear expediente', f'Creó el expediente {request.POST.get("exp", "")} - Actor: {request.POST.get("actor", "")} vs Demandado: {request.POST.get("demandado", "")} en {periodo_seleccionado}', request)
        
        messages.success(request, 'Expediente agregado correctamente.')
        return redirect(f"{reverse('bienvenida')}?periodo={periodo_seleccionado}")
    
    return render(request, 'agregar_expediente.html', {'periodo_actual': periodo_seleccionado})


def ver_expediente(request, id_expediente):
    if not request.session.get('empleado_id'):
        return redirect('iniciar_sesion')
    
    periodo_seleccionado = request.GET.get('periodo') or request.session.get('periodo_actual') or 'enero_2026'
    
    # Buscar en todas las tablas de periodo
    periodos = obtener_periodos_disponibles()
    expediente = None
    table_name = None
    
    for p in periodos:
        tabla = f"expediente_{p}"
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{tabla}` WHERE id = %s", [id_expediente])
            row = cursor.fetchone()
            if row:
                fields = [f.name for f in ConciliacionExpedientes._meta.fields]
                expediente = ExpedienteDinamico(row, tabla)
                table_name = tabla
                break
    
    if not expediente:
        messages.error(request, 'El expediente no existe.')
        return redirect(f"{reverse('bienvenida')}?periodo={periodo_seleccionado}")
    
    return render(request, 'ver_expediente.html', {'expediente': expediente, 'periodo_actual': periodo_seleccionado})

def editar_expediente(request, id_expediente):
    if not request.session.get('empleado_id'):
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=request.session['empleado_id'])
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirigir_a_error('No tienes permiso para realizar esta acción.')
    
    periodo_seleccionado = request.GET.get('periodo') or request.session.get('periodo_actual') or 'enero_2026'
    
    # Buscar en todas las tablas de periodo
    periodos = obtener_periodos_disponibles()
    expediente = None
    table_name = None
    
    for p in periodos:
        tabla = f"expediente_{p}"
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{tabla}` WHERE id = %s", [id_expediente])
            row = cursor.fetchone()
            if row:
                fields = [f.name for f in ConciliacionExpedientes._meta.fields]
                expediente = ExpedienteDinamico(row, tabla)
                table_name = tabla
                break
    
    if not expediente:
        messages.error(request, 'El expediente no existe.')
        return redirect(f"{reverse('bienvenida')}?periodo={periodo_seleccionado}")
    
    if request.method == 'POST':
        # Helper function to convert checkbox values
        def get_int_value(field_name):
            value = request.POST.get(field_name)
            return 1 if value == '1' or value == 'on' else None
        
        # Obtener valores del POST
        values = {
            'letra': request.POST.get('letra', ''),
            'exp': request.POST.get('exp', ''),
            'anio': request.POST.get('anio') or None,
            'actor': request.POST.get('actor', ''),
            'demandado': request.POST.get('demandado', ''),
            'area_en_la_que_se_encuentra': request.POST.get('area_en_la_que_se_encuentra', ''),
            'acuerdo_pendiente_de_caducidad': get_int_value('acuerdo_pendiente_de_caducidad'),
            'caducidad': get_int_value('caducidad'),
            'acuerdo_pendiente_prescripcion': get_int_value('acuerdo_pendiente_prescripcion'),
            'prescripcion': get_int_value('prescripcion'),
            'convenio_en_tramite': get_int_value('convenio_en_tramite'),
            'desistimiento': get_int_value('desistimiento'),
            'por_no_interpuesta': get_int_value('por_no_interpuesta'),
            'convenio_cumplimiento_laudo': get_int_value('convenio_cumplimiento_laudo'),
            'archivado_por_recision': get_int_value('archivado_por_recision'),
            'descentralizado': get_int_value('descentralizado'),
            'incompetencia': get_int_value('incompetencia'),
            'emplazamiento': get_int_value('emplazamiento'),
            'falta_not_actor_emplazamiento': get_int_value('falta_not_actor_emplazamiento'),
            'falta_emplazar': get_int_value('falta_emplazar'),
            'no_han_senalado': get_int_value('no_han_senalado'),
            'terminio': get_int_value('terminio'),
            'imposibilidad_emplazamiento': get_int_value('imposibilidad_emplazamiento'),
            'exhorto': get_int_value('exhorto'),
            'procedimiento': get_int_value('procedimiento'),
            'cita_conciliacion': get_int_value('cita_conciliacion'),
            'sin_cita_conciliacion': get_int_value('sin_cita_conciliacion'),
            'convenio_p_cumpl': get_int_value('convenio_p_cumpl'),
            'cde': get_int_value('cde'),
            'tercero_audiencia': get_int_value('tercero_audiencia'),
            'oap': get_int_value('oap'),
            'pruebas': get_int_value('pruebas'),
            'reserva': get_int_value('reserva'),
            'pendiente_revision': get_int_value('pendiente_revision'),
            'notificadas_ambas': get_int_value('notificadas_ambas'),
            'desahogo_pruebas': get_int_value('desahogo_pruebas'),
            'falta_citar_test': get_int_value('falta_citar_test'),
            'fata_not_partes': get_int_value('fata_not_partes'),
            'fuerza_publica_testimonial': get_int_value('fuerza_publica_testimonial'),
            'justificante': get_int_value('justificante'),
            'actora': get_int_value('actora'),
            'demandada': get_int_value('demandada'),
            'tercero': get_int_value('tercero'),
            'falta_designar_per': get_int_value('falta_designar_per'),
            'falta_not_partes_conf': get_int_value('falta_not_partes_conf'),
            'falta_ir_domicilio': get_int_value('falta_ir_domicilio'),
            'f_hacer_oficio': get_int_value('f_hacer_oficio'),
            'falta_girar_oficio': get_int_value('falta_girar_oficio'),
            'sin_respuesta': get_int_value('sin_respuesta'),
            'falta_inspeccion': get_int_value('falta_inspeccion'),
            'falta_cotejo': get_int_value('falta_cotejo'),
            'inc_nul_not': get_int_value('inc_nul_not'),
            'cierre': get_int_value('cierre'),
            'alegatos': get_int_value('alegatos'),
            'prueba_pendiente': get_int_value('prueba_pendiente'),
            'cierre_cierre': get_int_value('cierre_cierre'),
            'pendiente_de_laudo': get_int_value('pendiente_de_laudo'),
            'dictado': get_int_value('dictado'),
            'falta_not_partes_dictados': get_int_value('falta_not_partes_dictados'),
            'condenatorio': get_int_value('condenatorio'),
            'absolutorio': get_int_value('absolutorio'),
            'en_colegiado': get_int_value('en_colegiado'),
            'ejecucion': get_int_value('ejecucion'),
            'auto_ejecucion': get_int_value('auto_ejecucion'),
            'falta_not_actor_ejecucion': get_int_value('falta_not_actor_ejecucion'),
            'requerimiento': get_int_value('requerimiento'),
            'fuerza_publica_requerimiento': get_int_value('fuerza_publica_requerimiento'),
            'imposibilidad_requerimiento': get_int_value('imposibilidad_requerimiento'),
            'inembargable': get_int_value('inembargable'),
            'cuentas_embargadas': get_int_value('cuentas_embargadas'),
            'embargo_de_bien_inmueble_yo_muebles': get_int_value('embargo_de_bien_inmueble_yo_muebles'),
            'revision': get_int_value('revision'),
            'falta_reso_rev': get_int_value('falta_reso_rev'),
            'falta_not_partes_requerimiento': get_int_value('falta_not_partes_requerimiento'),
            'remate': get_int_value('remate'),
            'indirecto': get_int_value('indirecto'),
            'emplazar': get_int_value('emplazar'),
            'desahogo_pruebas_indirecto': get_int_value('desahogo_pruebas_indirecto'),
            'dictar_laudo': get_int_value('dictar_laudo'),
            'ejecucion_indirecto': get_int_value('ejecucion_indirecto'),
            'directo': get_int_value('directo')
        }
        
        # Actualizar en la tabla del periodo
        set_clause = ', '.join([f"`{k}` = %s" for k in values.keys()])
        query = f"UPDATE `{table_name}` SET {set_clause} WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, list(values.values()) + [id_expediente])
        
        registrar_accion(empleado, 'Editar expediente', f'Editó el expediente {values["exp"]} - Actor: {values["actor"]} vs Demandado: {values["demandado"]} en {periodo_seleccionado}', request)
        
        messages.success(request, 'Expediente actualizado correctamente.')
        return redirect(f"{reverse('bienvenida')}?periodo={periodo_seleccionado}")
    
    return render(request, 'editar_expediente.html', {'expediente': expediente, 'periodo_actual': periodo_seleccionado})


def crear_empleado(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.puede_gestionar_usuarios():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirigir_a_error('No tienes permiso para acceder a esta página.')

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
                tipo_puesto = obtener_etiqueta_puesto(puesto)
                registrar_accion(empleado, 'Crear empleado', f'Creó el empleado {nombre} (Clave: {clave_empleado}) como {tipo_puesto}', request)
                
                messages.success(request, 'Empleado creado exitosamente.')
                return redirect('crear_empleado')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    empleados = Empleado.objects.all()
    return render(request, 'crear_empleado.html', {
        'empleados': empleados,
        'roles': Empleado.Rol.choices,
    })


def eliminar_expediente(request, id_expediente):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.es_administrador():
        messages.error(request, 'No tienes permiso para eliminar expedientes.')
        return redirigir_a_error('No tienes permiso para eliminar expedientes.')
    
    periodo_seleccionado = request.GET.get('periodo') or request.session.get('periodo_actual') or 'enero_2026'
    
    # Buscar en todas las tablas de periodo
    periodos = obtener_periodos_disponibles()
    eliminado = False
    
    for p in periodos:
        tabla = f"expediente_{p}"
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{tabla}` WHERE id = %s", [id_expediente])
            row = cursor.fetchone()
            if row:
                cursor.execute(f"DELETE FROM `{tabla}` WHERE id = %s", [id_expediente])
                eliminado = True
                break
    
    if eliminado:
        messages.success(request, 'Expediente eliminado correctamente.')
    else:
        messages.error(request, 'El expediente no existe.')
    
    return redirect(f"{reverse('bienvenida')}?periodo={periodo_seleccionado}")


def editar_empleado(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    admin = Empleado.objects.get(id=empleado_id)
    if not admin.puede_gestionar_usuarios():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirigir_a_error('No tienes permiso para acceder a esta página.')

    empleado_edit = Empleado.objects.get(id=id)
    if request.method == 'POST':
        empleado_edit.nombre = request.POST.get('nombre')
        empleado_edit.clave_empleado = request.POST.get('clave_empleado')
        empleado_edit.puesto = request.POST.get('puesto')
        empleado_edit.save()
        
        # Registrar en bitácora
        tipo_puesto = obtener_etiqueta_puesto(empleado_edit.puesto)
        registrar_accion(admin, 'Editar empleado', f'Editó el empleado {empleado_edit.nombre} (Clave: {empleado_edit.clave_empleado}) - Puesto: {tipo_puesto}', request)
        
        messages.success(request, 'Empleado actualizado correctamente.')
        return redirect('crear_empleado')
    return render(request, 'editar_empleado.html', {
        'empleado': empleado_edit,
        'roles': Empleado.Rol.choices,
    })

def eliminar_empleado(request, id):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    admin = Empleado.objects.get(id=empleado_id)
    if not admin.puede_gestionar_usuarios():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirigir_a_error('No tienes permiso para acceder a esta página.')

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
        tipo_recepcion = request.POST.get('tipo_recepcion', 'usuario')
        nombre_carga = request.POST.get('nombre_carga', '').strip()
        nombre_carga_otro = request.POST.get('nombre_carga_otro', '').strip()
        junta_carga = request.POST.get('junta_carga', '').strip()

        if not empleado_id:
            return JsonResponse({'success': False, 'error': 'Sesión no iniciada'})

        if not expediente_id:
            return JsonResponse({'success': False, 'error': 'No se proporcionó el expediente'})

        if tipo_recepcion == 'usuario' and not nombre_carga:
            return JsonResponse({'success': False, 'error': 'Debes seleccionar un usuario'})

        if tipo_recepcion == 'otro' and (not nombre_carga_otro or not junta_carga):
            return JsonResponse({'success': False, 'error': 'Debes completar el nombre y la junta del receptor'})

        try:
            empleado = Empleado.objects.get(id=empleado_id)
            if not empleado.puede_cargar_expedientes():
                mensaje = 'No tienes permisos para realizar esta acción'
                return JsonResponse({
                    'success': False,
                    'error': mensaje,
                    'redirect_url': f"{reverse('error')}?mensaje={quote(mensaje)}",
                }, status=403)
            
            # Buscar expediente en todas las tablas de periodo
            periodos = obtener_periodos_disponibles()
            expediente = None
            table_name = None
            
            for p in periodos:
                tabla = f"expediente_{p}"
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT * FROM `{tabla}` WHERE id = %s", [expediente_id])
                    row = cursor.fetchone()
                    if row:
                        fields = [f.name for f in ConciliacionExpedientes._meta.fields]
                        expediente = ExpedienteDinamico(row, tabla)
                        table_name = tabla
                        break
            
            if not expediente:
                return JsonResponse({'success': False, 'error': 'El expediente no existe'})

            nombre_carga_guardar = ''
            junta_carga_guardar = ''

            if tipo_recepcion == 'usuario':
                try:
                    empleado_receptor = Empleado.objects.get(pk=int(nombre_carga))
                except (ValueError, TypeError, Empleado.DoesNotExist):
                    return JsonResponse({'success': False, 'error': 'Debes seleccionar un usuario válido'})

                if int(empleado_receptor.id) == int(empleado.id):
                    return JsonResponse({'success': False, 'error': 'No puedes cargar un expediente a tu propio usuario'})

                nombre_carga_guardar = empleado_receptor.nombre
            else:
                nombre_carga_guardar = nombre_carga_otro

            carga = CargaDescarga.objects.create(
                empleado=empleado,
                expediente_id=expediente_id,
                nombre_carga=nombre_carga_guardar,
                junta_carga=junta_carga_guardar,
            )

            registrar_accion(
                empleado,
                'Cargar expediente',
                f'Cargó el expediente {expediente.letra} {expediente.exp}/{expediente.anio} - {nombre_carga_guardar}' + (f' - Junta: {junta_carga_guardar}' if junta_carga_guardar else ''),
                request,
            )

            return JsonResponse({'success': True, 'id': carga.id})
        except Empleado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El empleado no existe'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def ver_cargas(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.puede_cargar_expedientes():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirigir_a_error('No tienes permiso para acceder a esta página.')
    
    cargas = CargaDescarga.objects.select_related('empleado').all().order_by('-fecha')
    return render(request, 'ver_cargas.html', {'cargas': cargas})


# Remove @login_required decorator and keep the function as is
def archivar_expediente(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return JsonResponse({'success': False, 'error': 'Sesión no iniciada'})
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.puede_archivar_expedientes():
        mensaje = 'No tienes permisos para realizar esta acción'
        return JsonResponse({
            'success': False,
            'error': mensaje,
            'redirect_url': f"{reverse('error')}?mensaje={quote(mensaje)}",
        }, status=403)

    if request.method == 'POST':
        try:
            expedientes_ids = request.POST.getlist('expedientes_ids[]')
            motivo = request.POST.get('motivo')
            
            if not expedientes_ids:
                return JsonResponse({'success': False, 'error': 'No se seleccionaron expedientes'})
            
            archivados_count = 0
            for expediente_id in expedientes_ids:
                try:
                    # Buscar en todas las tablas de periodo
                    periodos = obtener_periodos_disponibles()
                    expediente = None
                    table_name = None
                    
                    for p in periodos:
                        tabla = f"expediente_{p}"
                        with connection.cursor() as cursor:
                            cursor.execute(f"SELECT * FROM `{tabla}` WHERE id = %s", [expediente_id])
                            row = cursor.fetchone()
                            if row:
                                fields = [f.name for f in ConciliacionExpedientes._meta.fields]
                                expediente = ExpedienteDinamico(row, tabla)
                                table_name = tabla
                                break
                    
                    if expediente:
                        snapshot = {
                            'letra': expediente.letra,
                            'exp': expediente.exp,
                            'anio': expediente.anio,
                            'actor': expediente.actor,
                            'demandado': expediente.demandado,
                            'area_en_la_que_se_encuentra': expediente.area_en_la_que_se_encuentra,
                        }
                        
                        # Guardar el expediente completo para restauración posterior
                        Archivados.objects.create(
                            expediente=f"{expediente.letra or ''} {expediente.exp or ''}/{expediente.anio or ''}".strip(),
                            junta=expediente.area_en_la_que_se_encuentra or '',
                            actor=expediente.actor or '',
                            demandado=expediente.demandado or '',
                            motivo=motivo,
                            datos_expediente=snapshot,
                        )
                        
                        # Delete from original table
                        with connection.cursor() as cursor:
                            cursor.execute(f"DELETE FROM `{table_name}` WHERE id = %s", [expediente_id])
                        archivados_count += 1
                except Exception:
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
    if not empleado.puede_archivar_expedientes():
        mensaje = 'No tienes permisos para realizar esta acción'
        return JsonResponse({
            'success': False,
            'error': mensaje,
            'redirect_url': f"{reverse('error')}?mensaje={quote(mensaje)}",
        }, status=403)
    
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))
    
    search_query = request.GET.get('search', '').lower().strip()
    
    periodos = obtener_periodos_disponibles()
    expedientes_list = []
    
    for p in periodos:
        tabla = f"expediente_{p}"
        query = f"SELECT id, letra, exp, anio, actor, demandado, area_en_la_que_se_encuentra FROM `{tabla}`"
        params = []
        if search_query:
            query += " WHERE LOWER(CONCAT_WS(' ', COALESCE(letra,''), COALESCE(exp,''), COALESCE(CAST(anio AS CHAR),''), COALESCE(actor,''), COALESCE(demandado,''), COALESCE(area_en_la_que_se_encuentra,''))) LIKE %s"
            params = [f'%{search_query}%']
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                expedientes_list.append({
                    'id': row[0],
                    'expediente': f"{row[1] or ''} {row[2] or ''}/{row[3] or ''}".strip() or f"Exp. {row[0]}",
                    'junta': row[6],
                    'actor_nombre': row[4],
                    'demandado_nombre': row[5],
                })
    
    total = len(expedientes_list)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = expedientes_list[start:end]
    
    return JsonResponse({
        'success': True,
        'expedientes': page_data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': max(1, (total + page_size - 1) // page_size)
        }
    })

# Remove @login_required decorator and keep the function as is
def ver_archivados(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.puede_archivar_expedientes():
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirigir_a_error('No tienes permiso para acceder a esta página.')
    
    archivados = Archivados.objects.all().order_by('-fecha_archivo')
    return render(request, 'ver_archivados.html', {'archivados': archivados, 'empleado': empleado})

def exportar_expedientes_excel(request):
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        messages.error(request, 'Debes iniciar sesión')
        return redirect('iniciar_sesion')

    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.puede_exportar_expedientes():
        messages.error(request, 'No tienes permiso para exportar expedientes.')
        return redirigir_a_error('No tienes permiso para exportar expedientes.')
    
    wb = Workbook()

    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    campos_exportables = obtener_campos_exportables_expediente()
    headers = [etiqueta for _, etiqueta in campos_exportables]
    column_fields = [campo for campo, _ in campos_exportables]

    periodos = obtener_periodos_disponibles()

    for idx, periodo in enumerate(periodos):
        table_name = f"expediente_{periodo}"

        if idx == 0:
            ws = wb.active
            ws.title = periodo.replace('_', ' ').title()
        else:
            ws = wb.create_sheet(title=periodo.replace('_', ' ').title())

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            ws.column_dimensions[cell.column_letter].width = 12

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {', '.join(column_fields)} FROM `{table_name}`")
            for row_num, row in enumerate(cursor.fetchall(), 2):
                for col_num, value in enumerate(row, 1):
                    ws.cell(row=row_num, column=col_num).value = value or ''

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename=expedientes_{fecha_actual}.xlsx'

    wb.save(response)
    return response


def ver_bitacora(request):
    """Vista para mostrar la bitácora de acciones - solo para administradores"""
    empleado_id = request.session.get('empleado_id')
    if not empleado_id:
        return redirect('iniciar_sesion')
    
    empleado = Empleado.objects.get(id=empleado_id)
    if not empleado.puede_ver_bitacora():
        messages.error(request, 'No tienes permisos para ver la bitácora.')
        return redirigir_a_error('No tienes permisos para ver la bitácora.')
    
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
        if not empleado.puede_archivar_expedientes():
            mensaje = 'No tienes permisos para realizar esta acción'
            return JsonResponse({
                'success': False,
                'error': mensaje,
                'redirect_url': f"{reverse('error')}?mensaje={quote(mensaje)}",
            }, status=403)
        id_archivo = request.POST.get('id_archivo')
        
        if not id_archivo:
            return JsonResponse({'success': False, 'error': 'ID de archivo no proporcionado'})
        
        # Obtener el expediente archivado
        archivo = Archivados.objects.get(id_archivo=id_archivo)

        datos_expediente = archivo.datos_expediente or {}
        if not datos_expediente:
            datos_expediente = {
                'letra': None,
                'exp': archivo.expediente,
                'anio': None,
                'actor': archivo.actor,
                'demandado': archivo.demandado,
                'area_en_la_que_se_encuentra': archivo.junta,
            }
        
        periodo_seleccionado = request.session.get('periodo_actual') or 'enero_2026'
        crear_tabla_expediente_periodo(periodo_seleccionado)
        table_name = f"expediente_{periodo_seleccionado}"
        
        # Obtener el último id de la tabla del periodo
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT MAX(id) FROM `{table_name}`")
            last_id = cursor.fetchone()[0]
            new_id = 1 if last_id is None else last_id + 1
        
        # Campos y valores para INSERT
        fields = [f.name for f in ConciliacionExpedientes._meta.fields if f.name != 'id']
        values = [datos_expediente.get(f, None) for f in fields]
        
        query = f"INSERT INTO `{table_name}` ({', '.join([f'`{f}`' for f in fields])}) VALUES ({', '.join(['%s'] * len(fields))})"
        with connection.cursor() as cursor:
            cursor.execute(query, values)
        
        # Registrar en bitácora
        registrar_accion(
            empleado, 
            'Restaurar expediente', 
            f'Restauró el expediente {archivo.expediente} - Actor: {archivo.actor} vs Demandado: {archivo.demandado} en {periodo_seleccionado}',
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
        if not empleado.puede_gestionar_usuarios():
            mensaje = 'No tienes permisos para realizar esta acción'
            return JsonResponse({
                'success': False,
                'error': mensaje,
                'redirect_url': f"{reverse('error')}?mensaje={quote(mensaje)}",
            }, status=403)
        
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
