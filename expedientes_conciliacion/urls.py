from django.contrib import admin
from django.urls import path, include, re_path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),  # Incluir las URLs de la aplicación
    re_path(r'^(?!$).*', views.pagina_no_encontrada),
]

handler404 = 'app.views.pagina_no_encontrada'