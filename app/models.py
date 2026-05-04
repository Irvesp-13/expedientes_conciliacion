from django.db import models

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    clave_empleado = models.CharField(max_length=20, unique=True)
    puesto = models.IntegerField()  # 1: Administrador, 2: Usuario normal

    def __str__(self):
        return self.nombre

    def es_administrador(self):
        return self.puesto == 1

class ConciliacionExpedientes(models.Model):
    expediente = models.CharField(max_length=255, primary_key=True,db_column='EXPEDIENTE')
    junta = models.CharField(max_length=255, blank=True, null=True, db_column='JUNTA')
    tomo = models.CharField(max_length=255, blank=True, null=True, db_column='TOMO')
    actor_nombre = models.CharField(max_length=255, blank=True, null=True, db_column='ACTOR(NOMBRE)')
    mujer_numero = models.CharField(max_length=255, blank=True, null=True, db_column='MUJER (NUMERO)')
    hombre_numero = models.CharField(max_length=255, blank=True, null=True, db_column='HOMBRE(NUMERO)')
    demandado_nombre = models.CharField(max_length=255, blank=True, null=True, db_column='DEMANDADO (NOMBRE)')
    mujer_numero_0 = models.CharField(max_length=255, blank=True, null=True, db_column='MUJER (NUMERO)_[0]')
    hombre_numero_0 = models.CharField(max_length=255, blank=True, null=True, db_column='HOMBRE (NUMERO)')
    persona_moral_numero = models.CharField(max_length=255, blank=True, null=True, db_column='PERSONA MORAL (NUMERO)')
    iebem = models.CharField(max_length=255, blank=True, null=True, db_column='IEBEM')
    servicios_salud = models.CharField(max_length=255, blank=True, null=True, db_column='SERVICIOS SALUD')
    poder_ejecutivo = models.CharField(max_length=255, blank=True, null=True, db_column='PODER EJECUTIVO')
    ayuntamientos = models.CharField(max_length=255, blank=True, null=True, db_column='AYUNTAMIENTOS')
    otros_organismos = models.CharField(max_length=255, blank=True, null=True, db_column='OTROS ORGANISMOS')
    no_se_ha_notificado_a_las_partes = models.CharField(max_length=255, blank=True, null=True, db_column='NO SE HA NOTIFICACO A LAS PARTES')
    empl_no_realizado = models.CharField(max_length=255, blank=True, null=True, db_column='EMPL.NO REALIZADO')
    empl_exhorto = models.CharField(max_length=255, blank=True, null=True, db_column='EMPL. EXHORTO')
    exhortos_sin_enviar = models.CharField(max_length=255, blank=True, null=True, db_column='EXHORTOS SIN ENVIAR')
    exhortos_cdmx = models.CharField(max_length=255, blank=True, null=True, db_column='EXHORTOS CDMX')
    exhortos_foraneos = models.CharField(max_length=255, blank=True, null=True, db_column='EXHORTOS FORANEOS')
    cde = models.CharField(max_length=255, blank=True, null=True, db_column='C.D.E.')
    tercero_llamado_a_juicio = models.CharField(max_length=255, blank=True, null=True, db_column='TERCERO LLAMADO A JUICIO')
    oap = models.CharField(max_length=255, blank=True, null=True, db_column='O.A.P.')
    desahogo_pruebas = models.CharField(max_length=255, blank=True, null=True, db_column='DESAHOGO PRUEBAS')
    test_falta_citar = models.CharField(max_length=255, blank=True, null=True, db_column='TESTIMONIAL_FALTA_CITAR')
    periciales_partes = models.CharField(max_length=255, blank=True, null=True, db_column='PERICIALES_PARTES')
    pericial_tercero = models.CharField(max_length=255, blank=True, null=True, db_column='PERICIALES')
    inf_falta_hacer = models.CharField(max_length=255, blank=True, null=True, db_column='INFORME_FALTA_HACER')
    inf_falta_desahogar = models.CharField(max_length=255, blank=True, null=True, db_column='INFORME_FALTA_DESAHOGAR')
    otras_pruebas = models.CharField(max_length=255, blank=True, null=True, db_column='OTRAS_PRUEBAS')
    alegatos = models.CharField(max_length=255, blank=True, null=True, db_column='ALEGATOS')
    prueba_pendiente = models.CharField(max_length=255, blank=True, null=True, db_column='PRUEBA PENDIENTE')
    cierre = models.CharField(max_length=255, blank=True, null=True, db_column='CIERRE')
    laudo_dictado = models.CharField(max_length=255, blank=True, null=True, db_column='LAUDO DICTADO')
    absolutorio = models.CharField(max_length=255, blank=True, null=True, db_column='ABSOLUTORIO')
    condenatorio = models.CharField(max_length=255, blank=True, null=True, db_column='CONDENATORIO')
    monto = models.CharField(max_length=255, blank=True, null=True, db_column='MONTO DE CONDENA')
    auto_ejecucion = models.CharField(max_length=255, blank=True, null=True, db_column='AUTO EJECUCCION')
    terceria = models.CharField(max_length=255, blank=True, null=True, db_column='TERCERIA')
    recurso_revision = models.CharField(max_length=255, blank=True, null=True, db_column='RECURSO REVISION')
    remate = models.CharField(max_length=255, blank=True, null=True, db_column='REMATE')
    inactividad_1_anio = models.CharField(max_length=255, blank=True, null=True, db_column='INACTIVIDAD 1 ANIO')
    inactividad_2_anios_mas = models.CharField(max_length=255, blank=True, null=True, db_column='INACTIVIDAD 2 ANIOS O +')
    amparo_indirecto = models.CharField(max_length=255, blank=True, null=True, db_column='AMPARO INDIRECTO')
    amparo_directo_cumpl = models.CharField(max_length=255, blank=True, null=True, db_column='AMP. DIRECTO CUMPL.')
    sustitucion_patronal = models.CharField(max_length=255, blank=True, null=True, db_column='SUSTITUCION PATRONAL')
    no_interpuesta = models.CharField(max_length=255, blank=True, null=True, db_column='NO INTERPUESTA')
    prescripcion = models.CharField(max_length=255, blank=True, null=True, db_column='PRESCRIPCION')
    depuracion = models.CharField(max_length=255, blank=True, null=True, db_column='DEPURACION')
    regularizar = models.CharField(max_length=255, blank=True, null=True, db_column='REGULARIZAR')
    reviso_capturo = models.CharField(max_length=255, blank=True, null=True, db_column='REVISO CAPTURO')
    id_expediente = models.IntegerField(unique=True,db_column='id_expediente')

    class Meta:
        db_table = 'expedientes'  # Nombre de la tabla en MySQL
        managed = False  # Evita que Django intente gestionar la tabla

class DosMilSiete(models.Model):
    id_expediente = models.AutoField(unique=True, primary_key=True, db_column='id_expediente')
    expediente = models.CharField(max_length=255, db_column='EXPEDIENTE')
    junta = models.CharField(max_length=255, blank=True, null=False, db_column='JUNTA')
    actor = models.CharField(max_length=255, blank=True, null=False, db_column='ACTOR')
    demandado = models.CharField(max_length=255, blank=True, null=False, db_column='DEMANDADO')
    no_se_ha_notificao_a_las_partes = models.CharField(max_length=255, blank=True, null=True, db_column='NO SE HA NOTIFICACO A LAS PARTES')
    empl_no_realizado = models.CharField(max_length=255, blank=True, null=True, db_column='EMPL NO REALIZADO')
    empl_exhorto = models.CharField(max_length=255, blank=True, null=True, db_column='EMPL. EXHORTO')
    cde = models.CharField(max_length=255, blank=True, null=True, db_column='CDE')
    oap = models.CharField(max_length=255, blank=True, null=True, db_column='OAP')
    desahogo_pruebas = models.CharField(max_length=255, blank=True, null=True, db_column='DESAHOGO PRUEBAS')
    cierre = models.CharField(max_length=255, blank=True, null=True, db_column='CIERRE')
    laudo_dictado = models.CharField(max_length=255, blank=True, null=True, db_column='LAUDO DICTADO')
    auto_ejecucion = models.CharField(max_length=255, blank=True, null=True, db_column='AUTO EJECUCCION')
    prescripcion = models.CharField(max_length=255, blank=True, null=True, db_column='PRESCRIPCION')
    regularizar = models.CharField(max_length=255, blank=True, null=True, db_column='REGULARIZAR')

    class Meta:
        db_table = 'dosmilsiete'  # Nombre de la tabla en MySQL
        managed = False  # Evita que Django intente gestionar la tabla


class CargaDescarga(models.Model):
    id = models.AutoField(primary_key=True)  # This will auto-increment
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    expediente = models.ForeignKey(DosMilSiete, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    nombre_carga = models.CharField(max_length=255)

    class Meta:
        db_table = 'cargadescarga'


class Archivados(models.Model):
    id_archivo = models.AutoField(primary_key=True)
    expediente = models.CharField(max_length=255)  # Changed from ForeignKey to CharField
    junta = models.CharField(max_length=255)
    actor = models.CharField(max_length=255)
    demandado = models.CharField(max_length=255)
    fecha_archivo = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()

    class Meta:
        db_table = 'archivados'


class Bitacora(models.Model):
    id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=255)  # Tipo de acción (crear, editar, eliminar, etc.)
    descripcion = models.TextField()  # Descripción detallada de la acción
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'bitacora'
        ordering = ['-fecha_hora']

    def __str__(self):
        empleado_nombre = self.empleado.nombre if self.empleado else 'Usuario eliminado'
        return f"{self.fecha_hora} - {empleado_nombre} - {self.accion}"