from django.urls import path
from . import views

urlpatterns = [
    path('', views.iniciar_sesion, name='iniciar_sesion'),
    path('bienvenida/', views.bienvenida, name='bienvenida'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('agregar-expediente/', views.agregar_expediente, name='agregar_expediente'),
    path('ver-expediente/<int:id_expediente>/', views.ver_expediente, name='ver_expediente'),
    path('editar_expediente/<int:id_expediente>/', views.editar_expediente, name='editar_expediente'),
    path('crear-empleado/', views.crear_empleado, name='crear_empleado'),
    path('editar-empleado/<int:id>/', views.editar_empleado, name='editar_empleado'),
    path('eliminar-empleado/<int:id>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('cargar-expediente/', views.cargar_expediente, name='cargar_expediente'),
    path('ver-cargas/', views.ver_cargas, name='ver_cargas'),
    path('archivar-expediente/', views.archivar_expediente, name='archivar_expediente'),
    path('obtener-expedientes/', views.obtener_expedientes_ajax, name='obtener_expedientes_ajax'),
    path('ver-archivados/', views.ver_archivados, name='ver_archivados'),
    path('exportar-expedientes-excel/', views.exportar_expedientes_excel, name='exportar_expedientes_excel'),
    path('ver-bitacora/', views.ver_bitacora, name='ver_bitacora'),
    path('restaurar-expediente/', views.restaurar_expediente, name='restaurar_expediente'),
    path('eliminar-permanente/', views.eliminar_permanente, name='eliminar_permanente'),
]