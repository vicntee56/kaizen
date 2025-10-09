from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .models import Asistencia
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Task, Profile
from django.utils import timezone
from django.core.mail import send_mail
from .models import Profile
from django.utils import timezone
import random
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import SignInForm
from .forms import SignUpForm
from django.core.mail import send_mail
from django.utils import timezone
from .utils import generate_code, send_verification_email 
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from collections import Counter
import openpyxl
from django.contrib.auth.decorators import login_required
from .google_sheets_service import get_service
from .models import Reserva, Membresia
import pandas as pd
from django.http import HttpResponse
import os
from django.utils.timezone import localdate
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from datetime import date
from openpyxl import load_workbook
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import  timedelta
from .models import Horario, Reserva
from datetime import timedelta, time
from datetime import datetime
from django.utils.timezone import make_aware
from .forms import ExcelUploadForm
from .models import Profile, Reserva
from openpyxl.styles import PatternFill
from django import forms
from django.contrib import admin
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SolicitudDiasForm
from .models import Horario, Reserva, SolicitudDias
import os
from django.conf import settings
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from django.contrib.auth.decorators import login_required
import re 
from .models import Profile
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import Flow
from transbank.webpay.webpay_plus.transaction import Transaction




SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(
    os.path.join(settings.BASE_DIR, 'config/credentials.json'),
    scopes=SCOPES
)





Transaction.commerce_code = settings.TRANSBANK_COMMERCE_CODE
Transaction.api_key = settings.TRANSBANK_API_KEY
Transaction.integration_type = IntegrationType.TEST  # Cambia a .LIVE en producción

def retorno_pago(request):
    token = request.GET.get('token_ws')
    if not token:
        return render(request, 'fallo.html', {'error': 'Token no recibido'})

    try:
        response = Transaction.commit(token)
    except Exception as e:
        return render(request, 'fallo.html', {'error': str(e)})

    if response['status'] == 'AUTHORIZED':
        return render(request, 'exito.html', {
            'monto': response['amount'],
            'orden': response['buy_order']
        })
    else:
        return render(request, 'fallo.html', {'error': 'Pago rechazado'})

def seleccionar_plan(request):
    return render(request, 'pago.html')

def iniciar_pago(request):
    plan = request.GET.get('plan', 'mensual')
    precios = {
        'mensual': 63000,
        'trimestral': 170100,
        'semestral': 321300,
    }

    amount = precios.get(plan)
    if not amount:
        return render(request, 'error.html', {'mensaje': 'Plan inválido'})

    buy_order = f"orden-{plan}-{request.user.id}"
    session_id = f"sess-{request.user.id}"
    return_url = "http://127.0.0.1:8000/retorno/"  # Asegúrate de que esta URL exista

    options = WebpayOptions(
        commerce_code='597055555532',
        api_key='597055555532',
        integration_type=IntegrationType.TEST
    )

    tx = Transaction(options)
    response = tx.create(
        buy_order=buy_order,
        session_id=session_id,
        amount=amount,
        return_url=return_url
    )

    return redirect(f"{response['url']}?token_ws={response['token']}")








def generate_code():
    return str(random.randint(100000, 999999))



def index(request):
    return render(request, 'index.html')

@login_required
def verificar_codigo(request):
    user_profile = request.user.profile

    # Si ya está verificado, redirige directamente
    if user_profile.is_verified:
        messages.info(request, "Tu cuenta ya ha sido verificada.")
        return redirect('perfil')

    if request.method == 'POST':
        code = request.POST.get('verification_code')

        if (user_profile.verification_code == code and
            user_profile.token_expiry and
            user_profile.token_expiry > timezone.now()):
            
            user_profile.is_verified = True
            user_profile.save()

            messages.success(request, "¡Tu cuenta ha sido verificada exitosamente!")
            return redirect('perfil')
        else:
            messages.error(request, "El código es incorrecto o ha expirado. Solicita uno nuevo.")
            return redirect('verificar_codigo')

    # 🛠️ Este `return` es para el caso GET y cuando NO está verificado
    return render(request, 'verificar_codigo.html')

@login_required
def reenviar_codigo(request):
    user = request.user
    profile = user.profile

    # Si ya está verificado, no reenviar
    if profile.is_verified:
        messages.info(request, "Tu cuenta ya ha sido verificada, no necesitas un nuevo código.")
        return redirect('perfil')

    nuevo_codigo = generate_code()
    profile.verification_code = nuevo_codigo
    profile.code_created_at = timezone.now()
    profile.token_expiry = timezone.now() + timedelta(minutes=5)
    profile.save()

    send_verification_email(user.email, nuevo_codigo)

    messages.info(request, "Se ha enviado un nuevo código de verificación a tu correo.")
    return redirect('verificar_codigo')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get('email')

            # Verificar si ya existe un usuario con ese correo
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo ya está registrado.')
                return render(request, 'signup.html', {'form': form})

            # Crear el nuevo usuario (sin guardar aún)
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()

            # Procesar el archivo Excel si se sube
            excel_file = form.cleaned_data.get('excel_file')
            verification_code = generate_code()
            token_expiry = timezone.now() + timedelta(minutes=5)

            Profile.objects.create(
                user=user,
                excel_file=excel_file if excel_file else None,
                verification_code=verification_code,
                code_created_at=timezone.now(),
                token_expiry=token_expiry
            )

            # Iniciar sesión automáticamente
            login(request, user)

            # Enviar el correo de verificación
            send_verification_email(user.email, verification_code)

            messages.info(request, "Te hemos enviado un código de verificación a tu correo electrónico.")
            return redirect('verificar_codigo')
    else:
        form = SignUpForm()

    response = render(request, 'signup.html', {'form': form})
    response['Cache-Control'] = 'no-store'
    return response

def verify_email(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)

        if profile.token_expiry > timezone.now():
            profile.is_verified = True
            profile.save()

            return render(request, 'verified.html', {'message': '¡Tu cuenta ha sido verificada con éxito!'})
        else:
            # En lugar de renderizar error.html, redirigir a una página de error genérica
            messages.error(request, 'El código ha expirado. Por favor, solicita uno nuevo.')
            return redirect('signup')  # Redirigir a la página de registro o donde consideres adecuado

    except Profile.DoesNotExist:
        messages.error(request, 'Código de verificación no válido. Verifica que el enlace sea correcto.')
        return redirect('signup')  # Redirigir a la página de registro o donde consideres adecuado


def signout(request):
    logout(request)
    return redirect('index')


def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Primero inicia sesión
                login(request, user)

                # Luego verifica si está verificado
                if not user.profile.is_verified:
                    messages.warning(request, "Primero debes verificar tu cuenta con el código enviado a tu correo.")
                    return redirect('verificar_codigo')

                # Si ya está verificado, redirige normalmente
                next_url = request.GET.get('next', 'perfil')
                return redirect(next_url)
            else:
                form.add_error(None, 'Nombre de usuario o contraseña incorrectos')
    else:
        form = SignInForm()

    return render(request, 'signin.html', {'form': form})



def send_verification_email(email, code):
    subject = "Verificación de correo"
    message = f"Tu código de verificación es: {code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])




# Guarda estos datos en settings.py
GOOGLE_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'client_secret.json')  # tu archivo descargado
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']

@login_required
def google_auth(request):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=[
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets.readonly'
        ],
        redirect_uri='http://localhost:8000/oauth2callback/'
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return redirect(authorization_url)

# Callback para guardar credenciales
@login_required
def oauth2callback(request):
    state = request.session['state']
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=[
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets.readonly'
        ],
        state=state,
        redirect_uri='http://localhost:8000/oauth2callback/'
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials

    # Opcional: Guarda token en tu modelo Profile
    profile = request.user.profile
    profile.token = credentials.to_json()  # Necesitas un campo 'token' en tu modelo
    profile.save()

    return redirect('perfil')


@login_required
def perfil(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    reservas = Reserva.objects.filter(user=request.user)
    
    # Modifica esta parte para usar booleanos
    try:
        membresia = Membresia.objects.get(usuario=request.user, pagado=True)
    except Membresia.DoesNotExist:
        membresia = None
    
    mensaje_pago = None

    if membresia and membresia.fecha_expiracion:
        hoy = timezone.now().date()
        dias_restantes = (membresia.fecha_expiracion - hoy).days
        if 0 <= dias_restantes <= 2:
            mensaje_pago = f"⚠️ Te quedan {dias_restantes} día(s) para renovar tu membresía."
        elif dias_restantes < 0:
            mensaje_pago = "❌ Tu membresía ha expirado. Por favor, renueva para continuar."

    if request.method == 'POST':
        sheet_input = request.POST.get('sheet_id_or_url', '').strip()
        if sheet_input:
            # Extraer el ID de la hoja de cálculo
            sheet_id = extract_sheet_id(sheet_input)  # Implementa esta función
            if sheet_id:
                profile.sheet_id = sheet_id
                profile.save()
                return redirect('perfil')

    return render(request, 'perfil.html', {
        'profile': profile,
        'reservas': reservas,
        'mensaje_pago': mensaje_pago,
    })

def extract_sheet_id(url):
    """Versión más robusta con validación de formato de ID"""
    if not url:
        return None
    
    # Elimina posibles espacios y caracteres especiales al inicio/final
    url = url.strip()
    
    # Patrón regex para un ID válido de Google Sheets (aproximadamente)
    id_pattern = r'[a-zA-Z0-9-_]{20,}'
    
    # Caso 1: URL completa
    if 'docs.google.com/spreadsheets/d/' in url:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None
    
    # Caso 2: Parámetro id=
    elif 'id=' in url:
        match = re.search(r'[?&]id=([a-zA-Z0-9-_]+)', url)
        return match.group(1) if match else None
    
    # Caso 3: Es directamente un ID válido
    elif re.fullmatch(id_pattern, url):
        return url
    
    return None



def recuperar_contraseña(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('new_password1')
        password2 = request.POST.get('new_password2')

        if password1 != password2:
            return render(request, 'recuperar_contraseña.html', {'error': 'Las contraseñas no coinciden.'})

        try:
            User = get_user_model()
            user = User.objects.get(email=email)
            user.password = make_password(password1)
            user.save()
            return render(request, 'recuperar_contraseña.html', {'mensaje': 'Contraseña actualizada correctamente.'})
        except User.DoesNotExist:
            return render(request, 'recuperar_contraseña.html', {'error': 'No se encontró una cuenta con ese correo.'})

    return render(request, 'recuperar_contraseña.html')


# Mapeo de días a números
DIA_MAP = {
    'Lunes': 0,
    'Martes': 1,
    'Miércoles': 2,
    'Jueves': 3,
    'Viernes': 4,
}

@login_required
def seleccionar_opcion(request):
    if request.method == 'POST':
        opcion = request.POST.get('opcion')

        if opcion not in ['3', 'todos']:
            messages.error(request, 'Opción inválida.')
            return redirect('horario')

        solicitud, creada = SolicitudDias.objects.get_or_create(usuario=request.user)
        solicitud.opcion = opcion
        solicitud.aprobado = False  # Se requiere aprobación del superuser
        solicitud.save()

        messages.success(request, 'Solicitud enviada. Espera la aprobación del administrador.')
        return redirect('horario')


DIA_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

FRANJAS_HORARIAS = [
    ('09:00', '11:00'),
    ('11:00', '13:00'),
    ('18:00', '20:00'),
    ('20:00', '22:00'),
]

def horario(request):
    user = request.user
    puede_reservar = False

    if user.is_authenticated:
        try:
            profile = Profile.objects.get(user=user)
            puede_reservar = True
        except Profile.DoesNotExist:
            puede_reservar = False

    horarios_tabla = []

    for inicio, fin in FRANJAS_HORARIAS:
        fila = {
            'hora_inicio': inicio,
            'hora_fin': fin,
            'dias': []
        }
        for dia in DIA_SEMANA:
            horario_obj = Horario.objects.filter(
                hora_inicio=inicio,
                hora_fin=fin,
                dia=dia
            ).first()

            if horario_obj:
                reservas_count = Reserva.objects.filter(
                    horario=horario_obj,
                    aprobado=True
                ).count()

                # ✅ Sumar ocupados manuales
                usados = reservas_count + horario_obj.ocupados_manual

                fila['dias'].append({
                    'horario_id': horario_obj.id,
                    'dia': dia,
                    'reservas': usados,  # 👈 Esto se muestra como "ocupados"
                    'capacidad': horario_obj.capacidad
                })
            else:
                fila['dias'].append({
                    'horario_id': None,
                    'dia': dia,
                    'reservas': 0,
                    'capacidad': 5
                })

        horarios_tabla.append(fila)

    context = {
        'dias': DIA_SEMANA,
        'horarios_tabla': horarios_tabla,
        'puede_reservar': puede_reservar,
    }

    return render(request, 'horario.html', context)
# Vista para reservar varios días (POST con checkboxes)
@login_required
def reservar_horarios_varios(request):
    if request.method == 'POST':
        reservas = request.POST.getlist('reservas')

        if not reservas:
            messages.error(request, "Debes seleccionar al menos un horario.")
            return redirect('horario')

        # Extraer días seleccionados en esta solicitud
        dias_nuevos = []
        for r in reservas:
            try:
                horario_id, dia = r.split('|')
                dias_nuevos.append(dia)
            except ValueError:
                continue

        dias_nuevos_unicos = set(dias_nuevos)

        # Obtener opción del usuario (3 días o todos los días)
        try:
            solicitud = SolicitudDias.objects.get(usuario=request.user)
        except SolicitudDias.DoesNotExist:
            messages.error(request, "No tienes permiso para reservar.")
            return redirect('horario')

        # Días ya reservados (aprobados o pendientes)
        reservas_activas = Reserva.objects.filter(user=request.user)
        dias_reservados = set(reservas_activas.values_list('dia', flat=True))

        # ✅ REGLA 1: No repetir mismo día en la misma solicitud
        dias_contados = Counter(dias_nuevos)
        if any(count > 1 for count in dias_contados.values()):
            messages.error(request, "No puedes seleccionar el mismo día en diferentes horarios.")
            return redirect('horario')

        # ✅ REGLA 2: No repetir mismo día sumando reservas existentes
        repetidos = dias_nuevos_unicos.intersection(dias_reservados)
        if repetidos:
            messages.error(request, f"Ya tienes una reserva para estos días: {', '.join(repetidos)}")
            return redirect('horario')

        # ✅ REGLA 3: Si opción es 3 días, máximo 3 días distintos en total
        dias_totales = dias_reservados.union(dias_nuevos_unicos)
        if solicitud.opcion == '3' and len(dias_totales) > 3:
            messages.error(request, "No puedes reservar más de 3 días en total.")
            return redirect('horario')

        # Crear reservas nuevas solo si no hay error
        for r in reservas:
            horario_id, dia = r.split('|')
            horario_obj = get_object_or_404(Horario, id=horario_id)

            reservas_existentes = Reserva.objects.filter(
                horario=horario_obj,
                dia=dia,
                aprobado=True
            ).count()

            if reservas_existentes >= horario_obj.capacidad:
                continue

            # Evitar duplicadas exactas
            existe = Reserva.objects.filter(
                user=request.user,
                horario=horario_obj,
                dia=dia
            ).exists()

            if not existe:
                Reserva.objects.create(
                    user=request.user,
                    horario=horario_obj,
                    dia=dia,
                    aprobado=False
                )

        messages.success(request, "Reservas enviadas. Espera aprobación del administrador.")
        return redirect('horario')
@login_required
def admin_reservas(request):
    if not request.user.is_superuser:
        return redirect('index')

    reservas = Reserva.objects.filter(aprobado=False).order_by('fecha_reserva')
    return render(request, 'admin_reservas.html', {'reservas': reservas})

@login_required
def aprobar_reserva(request, reserva_id):
    if not request.user.is_superuser:
        return redirect('index')

    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.aprobado = True
    reserva.save()
    messages.success(request, 'Reserva aprobado.')
    return redirect('admin_reservas')

# Vista para que superusuario apruebe reservas pendientes
@login_required
@user_passes_test(lambda u: u.is_superuser)
def administrar_reservas(request):
    reservas_pendientes = Reserva.objects.filter(aprobado=False).order_by('user__username', 'dia', 'horario__hora_inicio')

    if request.method == 'POST':
        reservas_ids = request.POST.getlist('reservas')
        Reserva.objects.filter(id__in=reservas_ids).update(aprobado=True)
        messages.success(request, "Reservas aprobadas correctamente.")
        return redirect('administrar_reservas')

    context = {
        'reservas_pendientes': reservas_pendientes
    }
    return render(request, 'administrar_reservas.html', context)

@login_required
def admin_reservas(request):
    if not request.user.is_superuser:
        return redirect('index')

    reservas = Reserva.objects.filter(aprobado=False).order_by('fecha_reserva')
    return render(request, 'admin_reservas.html', {'reservas': reservas})

@login_required
def aprobar_reserva(request, reserva_id):
    if not request.user.is_superuser:
        return redirect('index')

    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.aprobado = True
    reserva.save()
    messages.success(request, 'Reserva aprobada.')
    return redirect('admin_reservas')


def obtener_fecha_segun_dia(nombre_dia):
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    hoy = datetime.today()
    dia_actual = hoy.weekday()  # 0 es lunes
    dia_objetivo = dias_semana.index(nombre_dia)
    diferencia = (dia_objetivo - dia_actual) % 7
    return (hoy + timedelta(days=diferencia)).date()


@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, user=request.user)
    reserva.delete()
    messages.success(request, 'Reserva cancelada exitosamente.')
    return redirect('perfil')  # Redirige al perfil del usuario


def ver_horarios(request):
    horarios = Horario.objects.all()  # Obtener todos los horarios disponibles
    return render(request, 'ver_horarios.html', {'horarios': horarios})


#calcualdora de ejercicios



# Estándares de fuerza por nivel (proporción de peso levantado / peso corporal)
estandares = {
    'press_banca': {
        'principiante': 0.5,
        'intermedio': 1.0,
        'avanzado': 1.5,
        'elite': 2.0,
    },
    'sentadilla': {
        'principiante': 0.75,
        'intermedio': 1.25,
        'avanzado': 1.75,
        'elite': 2.5,
    },
    'peso_muerto': {
        'principiante': 1.0,
        'intermedio': 1.5,
        'avanzado': 2.0,
        'elite': 2.75,
    },
    'press_militar': {
        'principiante': 0.35,
        'intermedio': 0.75,
        'avanzado': 1.0,
        'elite': 1.5,
    },
    'dominadas': {
        'principiante': 0,
        'intermedio': 5,
        'avanzado': 10,
        'elite': 15,
    }
}

def evaluar_nivel(peso_usuario, peso_levantado, ejercicio):
    if ejercicio == 'dominadas':
        reps = peso_levantado
        for nivel, reps_min in estandares['dominadas'].items():
            if reps < reps_min:
                return nivel
        return 'elite'
    else:
        ratio = peso_levantado / peso_usuario
        for nivel, r_min in estandares[ejercicio].items():
            if ratio < r_min:
                return nivel
        return 'elite'

def calcular_nivel(request):
    resultado = {}
    if request.method == 'POST':
        try:
            peso_usuario = float(request.POST.get('peso_usuario'))
            ejercicio = request.POST.get('ejercicio')
            if ejercicio == 'dominadas':
                reps = int(request.POST.get('reps'))
                nivel = evaluar_nivel(peso_usuario, reps, ejercicio)
            else:
                peso_levantado = float(request.POST.get('peso_levantado'))
                nivel = evaluar_nivel(peso_usuario, peso_levantado, ejercicio)

            resultado = {
                'ejercicio': ejercicio.replace("_", " ").capitalize(),
                'nivel': nivel
            }

        except (ValueError, TypeError):
            resultado = {'error': 'Por favor ingresa todos los valores correctamente.'}

    return render(request, 'calculadora.html', {'resultado': resultado})


@login_required
def obtener_excel(request):
    try:
        profile = request.user.profile
        excel_json = profile.excel_json or "{}"
        return JsonResponse({'excel_json': excel_json})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label="Selecciona un archivo Excel (.xlsx)")



# views.py (ejemplo en la vista donde haces la reserva)


def hacer_reserva(request, horario_id):
    horario = get_object_or_404(Horario, id=horario_id)
    total_reservas = Reserva.objects.filter(horario=horario).count()

    if total_reservas >= horario.max_reservas:
        return HttpResponseForbidden("Este horario ya está completo.")

    Reserva.objects.create(user=request.user, horario=horario)
    return redirect('perfil')

@user_passes_test(lambda u: u.is_superuser)
def ver_perfil_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    reservas = Reserva.objects.filter(user=usuario).select_related('horario')
    profile = Profile.objects.get(user=usuario)

    # Procesar Excel (igual que en tu vista perfil)
    excel_json = None
    if profile.excel_file and profile.excel_file.path:
        df = pd.read_excel(profile.excel_file.path).fillna("")
        excel_json = {
            'data': df.values.tolist(),
            'headers': list(df.columns),
        }

    return render(request, 'ver_perfil.html', {
        'usuario': usuario,
        'reservas': reservas,
        'excel_json': excel_json
    })


from django.core.paginator import Paginator
@login_required
@user_passes_test(lambda u: u.is_superuser)
def lista_asistencia(request):
    if request.method == 'POST':
        # Eliminar asistencia si se envía delete_id
        if 'delete_id' in request.POST:
            asistencia_id = request.POST.get('delete_id')
            asistencia = get_object_or_404(Asistencia, id=asistencia_id)
            asistencia.delete()
            return redirect('lista_asistencia')

        user_id = request.POST.get('user_id')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')

        if user_id:
            user = get_object_or_404(User, id=user_id)
            asistencia, created = Asistencia.objects.get_or_create(
                nombre=user.first_name,
                apellido=user.last_name,
                fecha=localdate(),
                defaults={'presente': True}
            )
            if not created:
                asistencia.presente = True
                asistencia.save()
        elif nombre and apellido:
            asistencia, created = Asistencia.objects.get_or_create(
                nombre=nombre,
                apellido=apellido,
                fecha=localdate(),
                defaults={'presente': True}
            )
            if not created:
                asistencia.presente = True
                asistencia.save()

        return redirect('lista_asistencia')

    usuarios = User.objects.filter(is_superuser=False)
    asistencias_hoy = Asistencia.objects.filter(fecha=localdate())

    # Obtener asistencias anteriores (excluyendo hoy)
    todas_asistencias = Asistencia.objects.exclude(fecha=localdate()).order_by('-fecha')

    # Agrupar asistencias por semanas
    semanas = []
    semana_actual = []
    semana_inicio = None

    for asistencia in todas_asistencias:
        fecha = asistencia.fecha
        if semana_inicio is None:
            semana_inicio = fecha - timedelta(days=fecha.weekday())
            semana_fin = semana_inicio + timedelta(days=6)

        if semana_inicio <= fecha <= semana_fin:
            semana_actual.append(asistencia)
        else:
            semanas.append(semana_actual)
            semana_actual = [asistencia]
            semana_inicio = fecha - timedelta(days=fecha.weekday())
            semana_fin = semana_inicio + timedelta(days=6)

    if semana_actual:
        semanas.append(semana_actual)

    paginator = Paginator(semanas, 1)  # Una semana por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Agrupar asistencias de la semana actual por fecha string (dd-mm-yyyy)
    historial = defaultdict(list)
    if page_obj.object_list:
        for asistencia in page_obj.object_list[0]:
            fecha_str = asistencia.fecha.strftime('%d-%m-%Y')
            historial[fecha_str].append(asistencia)

    fecha_hoy = localdate().strftime('%d-%m-%Y')

    return render(request, 'lista_asistencia.html', {
        'usuarios': usuarios,
        'asistencias': asistencias_hoy,
        'historial': historial,
        'page_obj': page_obj,
        'fecha_hoy': fecha_hoy,
    })

def quienes_somos(request):
    return render(request, 'quienes_somos.html')




def verificar_y_enviar_avisos():
    hoy = timezone.now().date()
    membresias = Membresia.objects.filter(pagado='si')

    for m in membresias:
        if m.fecha_expiracion:
            dias_restantes = (m.fecha_expiracion - hoy).days

            if dias_restantes <= 0:
                asunto = 'Tu membresía ha vencido'
                mensaje = (
                    f'Hola {m.usuario.first_name},\n\n'
                    'Tu membresía ha vencido. Por favor, realiza el pago para continuar disfrutando del servicio.'
                )
                enviar_correo(m.usuario.email, asunto, mensaje)

            elif dias_restantes <= 2:
                asunto = 'Tu membresía está por vencer'
                mensaje = (
                    f'Hola {m.usuario.first_name},\n\n'
                    f'Te recordamos que tu membresía vence en {dias_restantes} día(s). '
                    'No olvides renovar para evitar interrupciones en el servicio.'
                )
                enviar_correo(m.usuario.email, asunto, mensaje)

def enviar_correo(destinatario, asunto, mensaje):
    send_mail(
        asunto,
        mensaje,
        'vicentesuarez18k@gmail.com',
        [destinatario],
        fail_silently=False,
    )

def politica_privacidad(request):
    return render(request, 'privacidad.html')

