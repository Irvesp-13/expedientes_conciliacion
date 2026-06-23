import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expedientes_conciliacion.settings')
django.setup()

from django.db import connection

PERIODO = 'enero_2026'
TABLE_NAME = f'expediente_{PERIODO}'
CSV_PATH = 'ExpedientesEnero.csv'

# Intentar varias codificaciones
for encoding in ['utf-8-sig', 'latin-1', 'cp1252']:
    try:
        f = open(CSV_PATH, newline='', encoding=encoding)
        reader = csv.DictReader(f)
        rows = list(reader)
        f.close()
        break
    except UnicodeDecodeError:
        continue
else:
    raise ValueError("No se pudo leer el CSV con ninguna codificación")
    # Crear tabla si no existe (copiando estructura de tabla expediente base)
with connection.cursor() as cursor:
    cursor.execute(f"CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` LIKE `expediente`")

count = 0
for row in rows:
        id_val = int(row['id']) if row.get('id') else None
        
        # Campos con sus valores (convertir 1/0 o vacío/null)
        def parse_val(v):
            if v is None: return None
            v = str(v).strip()
            if v == '' or v.lower() in ('0',): return None
            if v == '1': return 1
            return v
        
        values = [
            id_val, parse_val(row.get('letra')), parse_val(row.get('exp')), parse_val(row.get('anio')),
            parse_val(row.get('actor')), parse_val(row.get('demandado')), parse_val(row.get('area_en_la_que_se_encuentra')),
            parse_val(row.get('acuerdo_pendiente_de_caducidad')), parse_val(row.get('caducidad')), parse_val(row.get('acuerdo_pendiente_prescripcion')), 
            parse_val(row.get('prescripcion')), parse_val(row.get('convenio_en_tramite')), parse_val(row.get('desistimiento')),
            parse_val(row.get('por_no_interpuesta')), parse_val(row.get('convenio_cumplimiento_laudo')), parse_val(row.get('archivado_por_recision')),
            parse_val(row.get('descentralizado')), parse_val(row.get('incompetencia')), parse_val(row.get('emplazamiento')),
            parse_val(row.get('falta_not_actor_emplazamiento')), parse_val(row.get('falta_emplazar')), parse_val(row.get('no_han_senalado')),
            parse_val(row.get('terminio')), parse_val(row.get('imposibilidad_emplazamiento')), parse_val(row.get('exhorto')),
            parse_val(row.get('procedimiento')), parse_val(row.get('cita_conciliacion')), parse_val(row.get('sin_cita_conciliacion')),
            parse_val(row.get('convenio_p_cumpl')), parse_val(row.get('cde')), parse_val(row.get('tercero_audiencia')),
            parse_val(row.get('oap')), parse_val(row.get('pruebas')), parse_val(row.get('reserva')),
            parse_val(row.get('pendiente_revision')), parse_val(row.get('notificadas_ambas')), parse_val(row.get('desahogo_pruebas')),
            parse_val(row.get('falta_citar_test')), parse_val(row.get('fata_not_partes')), parse_val(row.get('fuerza_publica_testimonial')),
            parse_val(row.get('justificante')), parse_val(row.get('actora')), parse_val(row.get('demandada')),
            parse_val(row.get('tercero')), parse_val(row.get('falta_designar_per')), parse_val(row.get('falta_not_partes_conf')),
            parse_val(row.get('falta_ir_domicilio')), parse_val(row.get('f_hacer_oficio')), parse_val(row.get('falta_girar_oficio')),
            parse_val(row.get('sin_respuesta')), parse_val(row.get('falta_inspeccion')), parse_val(row.get('falta_cotejo')),
            parse_val(row.get('inc_nul_not')), parse_val(row.get('cierre')), parse_val(row.get('alegatos')),
            parse_val(row.get('prueba_pendiente')), parse_val(row.get('cierre_cierre')), parse_val(row.get('pendiente_de_laudo')),
            parse_val(row.get('dictado')), parse_val(row.get('falta_not_partes_dictados')), parse_val(row.get('condenatorio')),
            parse_val(row.get('absolutorio')), parse_val(row.get('en_colegiado')), parse_val(row.get('ejecucion')),
            parse_val(row.get('auto_ejecucion')), parse_val(row.get('falta_not_actor_ejecucion')), parse_val(row.get('requerimiento')),
            parse_val(row.get('fuerza_publica_requerimiento')), parse_val(row.get('imposibilidad_requerimiento')), parse_val(row.get('inembargable')),
            parse_val(row.get('cuentas_embargadas')), parse_val(row.get('embargo_de_bien_inmueble_yo_muebles')), parse_val(row.get('revision')),
            parse_val(row.get('falta_reso_rev')), parse_val(row.get('falta_not_partes_requerimiento')), parse_val(row.get('remate')),
            parse_val(row.get('indirecto')), parse_val(row.get('emplazar')), parse_val(row.get('desahogo_pruebas_indirecto')),
            parse_val(row.get('dictar_laudo')), parse_val(row.get('ejecucion_indirecto')), parse_val(row.get('directo'))
        ]
        
        fields = ['id', 'letra', 'exp', 'anio', 'actor', 'demandado', 'area_en_la_que_se_encuentra',
            'acuerdo_pendiente_de_caducidad', 'caducidad', 'acuerdo_pendiente_prescripcion', 'prescripcion',
            'convenio_en_tramite', 'desistimiento', 'por_no_interpuesta', 'convenio_cumplimiento_laudo', 'archivado_por_recision',
            'descentralizado', 'incompetencia', 'emplazamiento', 'falta_not_actor_emplazamiento', 'falta_emplazar',
            'no_han_senalado', 'terminio', 'imposibilidad_emplazamiento', 'exhorto', 'procedimiento',
            'cita_conciliacion', 'sin_cita_conciliacion', 'convenio_p_cumpl', 'cde', 'tercero_audiencia',
            'oap', 'pruebas', 'reserva', 'pendiente_revision', 'notificadas_ambas', 'desahogo_pruebas',
            'falta_citar_test', 'fata_not_partes', 'fuerza_publica_testimonial', 'justificante', 'actora', 'demandada',
            'tercero', 'falta_designar_per', 'falta_not_partes_conf', 'falta_ir_domicilio', 'f_hacer_oficio',
            'falta_girar_oficio', 'sin_respuesta', 'falta_inspeccion', 'falta_cotejo', 'inc_nul_not', 'cierre',
            'alegatos', 'prueba_pendiente', 'cierre_cierre', 'pendiente_de_laudo', 'dictado',
            'falta_not_partes_dictados', 'condenatorio', 'absolutorio', 'en_colegiado', 'ejecucion',
            'auto_ejecucion', 'falta_not_actor_ejecucion', 'requerimiento', 'fuerza_publica_requerimiento',
            'imposibilidad_requerimiento', 'inembargable', 'cuentas_embargadas', 'embargo_de_bien_inmueble_yo_muebles',
            'revision', 'falta_reso_rev', 'falta_not_partes_requerimiento', 'remate', 'indirecto', 'emplazar',
            'desahogo_pruebas_indirecto', 'dictar_laudo', 'ejecucion_indirecto', 'directo']
        
        placeholders = ', '.join(['%s'] * len(values))
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO `{TABLE_NAME}` ({', '.join([f'`{f}`' for f in fields])}) VALUES ({placeholders})",
                values
            )
        count += 1
        print(f"Importado: {row.get('letra', '')} {row.get('exp', '')}/{row.get('anio', '')}")

print(f"\nImportados {count} expedientes en {TABLE_NAME}")