from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views







urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Páginas principales
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='login'),  # Usamos 'login' como nombre estándar
    path('logout/', views.signout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('horario/', views.horario, name='horario'),
    path('cancelar_reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('calculadora/', views.calcular_nivel, name='calculadora'),
    path('admin/ver_perfil/<int:user_id>/', views.ver_perfil_usuario, name='ver_perfil_usuario'),
    path('reservar-varios/', views.reservar_horarios_varios, name='reservar_horarios_varios'),
    path('authorize/', views.google_auth, name='google_auth'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),

    # Verificación de correo
    path('verify/<uuid:token>/', views.verify_email, name='verify_email'),
    path('verificar_codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('reenviar-codigo/', views.reenviar_codigo, name='reenviar_codigo'),

    # Recuperación de contraseña con vistas integradas de Django
    path('recuperar/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('recuperar/completo/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Pago de Tranbank
    path('pagar/', views.iniciar_pago, name='pagar'),
    path('retorno/', views.retorno_pago, name='retorno_pago'),
    path('seleccionar-plan/', views.seleccionar_plan, name='seleccionar_plan'),
    path('asistencia/', views.lista_asistencia, name='lista_asistencia'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
]

# Para servir archivos subidos (como Excel)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
