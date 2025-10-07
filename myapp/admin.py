from django.contrib import admin
from .models import Horario, Reserva, SolicitudDias
from .models import Membresia, Invitado
from django import forms
from django.core.exceptions import ValidationError
from .models import Horario
from .models import Visita
# Admin para Task





# Acciones personalizadas para reservas
@admin.action(description="Aprobar reservas seleccionadas")
def aprobar_reservas(modeladmin, request, queryset):
    queryset.update(aprobado=True)

@admin.action(description="Cancelar reservas seleccionadas")
def cancelar_reservas(modeladmin, request, queryset):
    queryset.delete()


# ✅ Admin para Reserva
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido_usuario', 'dia', 'horario_hora', 'aprobado', 'fecha_reserva')
    list_filter = ('aprobado', 'dia', 'horario')
    search_fields = ('user__username', 'dia')
    actions = [aprobar_reservas, cancelar_reservas]

    def nombre_apellido_usuario(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.username})"
    nombre_apellido_usuario.short_description = 'Usuario'

    def horario_hora(self, obj):
        return f"{obj.horario.hora_inicio.strftime('%H:%M')} - {obj.horario.hora_fin.strftime('%H:%M')}"
    horario_hora.short_description = 'Horario'

admin.site.register(Reserva, ReservaAdmin)



@admin.register(SolicitudDias)
class SolicitudDiasAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido_usuario', 'opcion')
    list_editable = ('opcion',)

    def nombre_apellido_usuario(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name} ({obj.usuario.username})"
    nombre_apellido_usuario.short_description = 'Usuario'



class MembresiaForm(forms.ModelForm):
    class Meta:
        model = Membresia  # Asegúrate que este nombre coincida con tu modelo
        fields = '__all__'
        widgets = {
            'pagado': forms.CheckboxInput(attrs={
                'class': 'pagado-checkbox',
                'onchange': 'document.getElementById("id_no_pagado").checked = !this.checked;'
            }),
            'no_pagado': forms.CheckboxInput(attrs={
                'class': 'no-pagado-checkbox',
                'onchange': 'document.getElementById("id_pagado").checked = !this.checked;'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('pagado') and cleaned_data.get('no_pagado'):
            raise ValidationError("No puede estar Pagado y No Pagado simultáneamente")
        return cleaned_data

from django.utils import timezone

@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    form = MembresiaForm
    list_display = ('usuario_completo', 'estado_pago', 'plan', 'fecha_inicio', 'fecha_expiracion')
    list_filter = ('pagado', 'plan')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'usuario__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        hoy = timezone.now().date()
        for m in qs:
            if m.fecha_expiracion and m.fecha_expiracion < hoy and m.pagado:
                m.pagado = False
                m.save()
        return qs


    def usuario_completo(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name} ({obj.usuario.username})"
    usuario_completo.short_description = 'Usuario'  # Nombre de la columna
    usuario_completo.admin_order_field = 'usuario__first_name'  # Permite ordenar
    
    # Método para estado de pago con iconos
    def estado_pago(self, obj):
        from django.utils.html import format_html
        if obj.pagado:
            return format_html('<span style="color: green;">✓ Pagado</span>')
        return format_html('<span style="color: red;">✗ No pagado</span>')
    estado_pago.short_description = 'Estado'
    

    class Media:
        css = {
            'all': ('membresia.css',)
        }
        js = ('admin/js/membresia.js',)

# ==========================
# ✅ Admin para Invitado
# ==========================
@admin.register(Invitado)
class InvitadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'plan', 'pagado', 'fecha_inicio', 'fecha_expiracion')
    list_editable = ('plan', 'pagado')
    search_fields = ('nombre', 'apellido')

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('dia', 'hora_inicio_24h', 'hora_fin_24h', 'capacidad', 'ocupados_manual')

    def hora_inicio_24h(self, obj):
        return obj.hora_inicio.strftime('%H:%M')
    hora_inicio_24h.short_description = 'Hora de inicio'

    def hora_fin_24h(self, obj):
        return obj.hora_fin.strftime('%H:%M')
    hora_fin_24h.short_description = 'Hora fin'

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('ip', 'ciudad', 'region', 'fecha')
    list_filter = ('ciudad', 'region')
    search_fields = ('ip', 'ciudad', 'region')

