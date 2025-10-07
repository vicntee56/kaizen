from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import time
from dateutil.relativedelta import relativedelta  # ✅ Importa esto
from datetime import timedelta
from django.core.exceptions import ValidationError  # Importación añadida




class Task(models.Model):
    title = models.CharField(max_length=200)
    descriptions = models.TextField(blank=200)
    created = models.DateField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ' - by ' + self.user.username

# NUEVO MODELO PARA VERIFICACIÓN DE USUARIO




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4)
    token_expiry = models.DateTimeField(null=True, blank=True)
    verification_code = models.CharField(max_length=6, default='000000')
    code_created_at = models.DateTimeField(default=timezone.now)
    excel_file = models.FileField(upload_to='excels/', null=True, blank=True)
    excel_json = models.TextField(null=True, blank=True)
    sheet_id = models.CharField(max_length=200, blank=True, null=True)
    gmail = models.EmailField(blank=True, null=True)

    token = models.TextField(blank=True, null=True)

    OPCIONES_TIPO_RESERVA = (
        ('3', '3 días'),
        ('todos', 'Todos los días'),
    )
    tipo_reserva = models.CharField(
        max_length=10,
        choices=OPCIONES_TIPO_RESERVA,
        default='3'
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"







# Modelo de los horarios disponibles
class Horario(models.Model):
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    dia = models.CharField(max_length=20)
    capacidad = models.IntegerField(default=5)
    ocupados_manual = models.IntegerField(default=0)

    class Meta:
        unique_together = ('dia', 'hora_inicio', 'hora_fin')

    def __str__(self):
        return f"{self.dia} {self.hora_inicio} - {self.hora_fin}"
    

# Modelo de reserva de horarios por los usuarios
class Reserva(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    dia = models.CharField(max_length=20, default='Pendiente', blank=True)
    aprobado = models.BooleanField(default=False)
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.dia} - {self.horario}"





class SolicitudDias(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    aprobado = models.BooleanField(default=False)

    OPCIONES = (
        ('3', '3 días'),
        ('todos', 'Todos los días'),
    )
    opcion = models.CharField(max_length=10, choices=OPCIONES, default='3')

    def __str__(self):
        return f"{self.usuario.username} ({self.opcion})"

class Asistencia(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha = models.DateField()  # solo fecha
    presente = models.BooleanField(default=False)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.fecha} - {'Presente' if self.presente else 'Ausente'}"
    



PLANES = [
    ('Mensual', 'Mensual'),
    ('Trimestral', 'Trimestral'),
    ('Semestral', 'Semestral'),
]

class Membresia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False, verbose_name="Pagado")
    no_pagado = models.BooleanField(default=True, verbose_name="No Pagado", editable=False)
    plan = models.CharField(max_length=20, choices=PLANES)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_expiracion = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Sincronización automática
        if self.pagado:
            self.no_pagado = False
        else:
            self.no_pagado = True
            
        hoy = timezone.now().date()
        
        if self.pagado:
            if not self.fecha_inicio:
                self.fecha_inicio = hoy
                
            if self.plan == 'Mensual':
                self.fecha_expiracion = self.fecha_inicio + relativedelta(months=1)
            elif self.plan == 'Trimestral':
                self.fecha_expiracion = self.fecha_inicio + relativedelta(months=3)
            elif self.plan == 'Semestral':
                self.fecha_expiracion = self.fecha_inicio + relativedelta(months=6)
        else:
            self.fecha_inicio = None
            self.fecha_expiracion = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} - {'Pagado' if self.pagado else 'No Pagado'}"
    

PLANES = [
    ('mensual', 'Mensual'),
    ('trimestral', 'Trimestral'),
    ('semestral', 'Semestral'),
]

class Invitado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    plan = models.CharField(max_length=20, choices=PLANES, default='mensual')
    pagado = models.BooleanField(default=False)
    fecha_inicio = models.DateField(editable=False, null=True, blank=True)
    fecha_expiracion = models.DateField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Asigna fecha de inicio si no existe
        if not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()

        # Siempre recalcula fecha de expiración en base al plan actual
        if self.plan == 'mensual':
            self.fecha_expiracion = self.fecha_inicio + timedelta(days=30)
        elif self.plan == 'trimestral':
            self.fecha_expiracion = self.fecha_inicio + timedelta(days=90)
        elif self.plan == 'semestral':
            self.fecha_expiracion = self.fecha_inicio + timedelta(days=180)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    # myapp/models.py
from django.db import models

class Visita(models.Model):
    ip = models.GenericIPAddressField()
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip} - {self.ciudad}, {self.region} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
