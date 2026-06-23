from django.db import models, connection

def crear_tabla_expediente_periodo(periodo):
    """
    Crea la tabla de expedientes para el periodo especificado.
    Tablas se llaman: expediente_enero_2026, expediente_febrero_2026, etc.
    """
    table_name = f"expediente_{periodo}"
    
    with connection.cursor() as cursor:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        tabla_existe = cursor.fetchone() is not None
    
    if not tabla_existe:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE `{table_name}` LIKE `expediente`
            """)

def obtener_periodos_disponibles():
    """Obtiene lista de periodos que tienen tablas creadas"""
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'expediente_%'")
        tablas = cursor.fetchall()
    
    periodos = []
    for tabla in tablas:
        nombre_tabla = tabla[0]
        periodo = nombre_tabla.replace('expediente_', '')
        periodos.append(periodo)
    
    return sorted(periodos, reverse=True)

def get_periodo_actual(request):
    """Obtiene el periodo actual de la sesión o devuelve el predeterminado"""
    periodo = request.session.get('periodo_actual')
    if not periodo:
        return 'enero_2026'
    return periodo

def set_periodo_actual(request, periodo):
    """Establece el periodo actual en la sesión"""
    request.session['periodo_actual'] = periodo

class Empleado(models.Model):
    class Rol(models.IntegerChoices):
        ADMINISTRADOR = 1, 'Administrador'
        EMPLEADO_A = 2, 'Empleado A'
        EMPLEADO_B = 3, 'Empleado B'

    usuario = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    clave_empleado = models.CharField(max_length=20, unique=True)
    rol = models.PositiveSmallIntegerField(choices=Rol.choices)
    id_plaza = models.CharField(max_length=20, blank=True, null=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre

    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR

    def es_empleado_a(self):
        return self.rol == self.Rol.EMPLEADO_A

    def es_empleado_b(self):
        return self.rol == self.Rol.EMPLEADO_B

    def puede_cargar_expedientes(self):
        return self.rol in {
            self.Rol.ADMINISTRADOR,
            self.Rol.EMPLEADO_A,
            self.Rol.EMPLEADO_B,
        }

    def puede_archivar_expedientes(self):
        return self.rol in {
            self.Rol.ADMINISTRADOR,
            self.Rol.EMPLEADO_A,
        }

    def puede_gestionar_usuarios(self):
        return self.es_administrador()

    def puede_ver_bitacora(self):
        return self.es_administrador()

    def puede_exportar_expedientes(self):
        return self.es_administrador()

class ConciliacionExpedientes(models.Model):
    id = models.AutoField(primary_key=True)
    letra = models.CharField(max_length=255, blank=True, null=True)
    exp = models.CharField(max_length=255, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    actor = models.CharField(max_length=255, blank=True, null=True)
    demandado = models.CharField(max_length=255, blank=True, null=True)
    area_en_la_que_se_encuentra = models.CharField(max_length=255, blank=True, null=True)
    acuerdo_pendiente_de_caducidad = models.IntegerField(blank=True, null=True)
    caducidad = models.IntegerField(blank=True, null=True)
    acuerdo_pendiente_prescripcion = models.IntegerField(blank=True, null=True)
    prescripcion = models.IntegerField(blank=True, null=True)
    convenio_en_tramite = models.IntegerField(blank=True, null=True)
    desistimiento = models.IntegerField(blank=True, null=True)
    por_no_interpuesta = models.IntegerField(blank=True, null=True)
    convenio_cumplimiento_laudo = models.IntegerField(blank=True, null=True)
    archivado_por_recision = models.IntegerField(blank=True, null=True)
    descentralizado = models.IntegerField(blank=True, null=True)
    incompetencia = models.IntegerField(blank=True, null=True)
    emplazamiento = models.IntegerField(blank=True, null=True)
    falta_not_actor_emplazamiento = models.IntegerField(blank=True, null=True)
    falta_emplazar = models.IntegerField(blank=True, null=True)
    no_han_senalado = models.IntegerField(blank=True, null=True)
    terminio = models.IntegerField(blank=True, null=True)
    imposibilidad_emplazamiento = models.IntegerField(blank=True, null=True)
    exhorto = models.IntegerField(blank=True, null=True)
    procedimiento = models.IntegerField(blank=True, null=True)
    cita_conciliacion = models.IntegerField(blank=True, null=True)
    sin_cita_conciliacion = models.IntegerField(blank=True, null=True)
    convenio_p_cumpl = models.IntegerField(blank=True, null=True)
    cde = models.IntegerField(blank=True, null=True)
    tercero_audiencia = models.IntegerField(blank=True, null=True)
    oap = models.IntegerField(blank=True, null=True)
    pruebas = models.IntegerField(blank=True, null=True)
    reserva = models.IntegerField(blank=True, null=True)
    pendiente_revision = models.IntegerField(blank=True, null=True)
    notificadas_ambas = models.IntegerField(blank=True, null=True)
    desahogo_pruebas = models.IntegerField(blank=True, null=True)
    falta_citar_test = models.IntegerField(blank=True, null=True)
    fata_not_partes = models.IntegerField(blank=True, null=True)
    fuerza_publica_testimonial = models.IntegerField(blank=True, null=True)
    justificante = models.IntegerField(blank=True, null=True)
    actora = models.IntegerField(blank=True, null=True)
    demandada = models.IntegerField(blank=True, null=True)
    tercero = models.IntegerField(blank=True, null=True)
    falta_designar_per = models.IntegerField(blank=True, null=True)
    falta_not_partes_conf = models.IntegerField(blank=True, null=True)
    falta_ir_domicilio = models.IntegerField(blank=True, null=True)
    f_hacer_oficio = models.IntegerField(blank=True, null=True)
    falta_girar_oficio = models.IntegerField(blank=True, null=True)
    sin_respuesta = models.IntegerField(blank=True, null=True)
    falta_inspeccion = models.IntegerField(blank=True, null=True)
    falta_cotejo = models.IntegerField(blank=True, null=True)
    inc_nul_not = models.IntegerField(blank=True, null=True)
    cierre = models.IntegerField(blank=True, null=True)
    alegatos = models.IntegerField(blank=True, null=True)
    prueba_pendiente = models.IntegerField(blank=True, null=True)
    cierre_cierre = models.IntegerField(blank=True, null=True)
    pendiente_de_laudo = models.IntegerField(blank=True, null=True)
    dictado = models.IntegerField(blank=True, null=True)
    falta_not_partes_dictados = models.IntegerField(blank=True, null=True)
    condenatorio = models.IntegerField(blank=True, null=True)
    absolutorio = models.IntegerField(blank=True, null=True)
    en_colegiado = models.IntegerField(blank=True, null=True)
    ejecucion = models.IntegerField(blank=True, null=True)
    auto_ejecucion = models.IntegerField(blank=True, null=True)
    falta_not_actor_ejecucion = models.IntegerField(blank=True, null=True)
    requerimiento = models.IntegerField(blank=True, null=True)
    fuerza_publica_requerimiento = models.IntegerField(blank=True, null=True)
    imposibilidad_requerimiento = models.IntegerField(blank=True, null=True)
    inembargable = models.IntegerField(blank=True, null=True)
    cuentas_embargadas = models.IntegerField(blank=True, null=True)
    embargo_de_bien_inmueble_yo_muebles = models.IntegerField(blank=True, null=True)
    revision = models.IntegerField(blank=True, null=True)
    falta_reso_rev = models.IntegerField(blank=True, null=True)
    falta_not_partes_requerimiento = models.IntegerField(blank=True, null=True)
    remate = models.IntegerField(blank=True, null=True)
    indirecto = models.IntegerField(blank=True, null=True)
    emplazar = models.IntegerField(blank=True, null=True)
    desahogo_pruebas_indirecto = models.IntegerField(blank=True, null=True)
    dictar_laudo = models.IntegerField(blank=True, null=True)
    ejecucion_indirecto = models.IntegerField(blank=True, null=True)
    directo = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'expediente'

    def __str__(self):
        partes = [self.letra, self.exp, str(self.anio) if self.anio is not None else None]
        identificador = ' '.join(parte for parte in partes if parte)
        return identificador or f'Expediente {self.pk}'


class CargaDescarga(models.Model):
    id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    expediente_id = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    nombre_carga = models.CharField(max_length=255)
    junta_carga = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'cargadescarga'


class Archivados(models.Model):
    id_archivo = models.AutoField(primary_key=True)
    expediente = models.CharField(max_length=255)
    junta = models.CharField(max_length=255)
    actor = models.CharField(max_length=255)
    demandado = models.CharField(max_length=255)
    fecha_archivo = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    datos_expediente = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'archivados'


class Bitacora(models.Model):
    id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'bitacora'
        ordering = ['-fecha_hora']

    def __str__(self):
        empleado_nombre = self.empleado.nombre if self.empleado else 'Usuario eliminado'
        return f"{self.fecha_hora} - {empleado_nombre} - {self.accion}"


# Meses en español
MESES_ESPANOL = {
    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
    5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
}