from background_task import background
from django.utils import timezone
from myapp.models import Membresia

@background()
def actualizar_membresias():
    """
    Marca como no pagadas todas las membresías cuya fecha_expiracion ya venció.
    """
    hoy = timezone.now().date()
    vencidas = Membresia.objects.filter(fecha_expiracion__lt=hoy, pagado=True)

    for m in vencidas:
        m.pagado = False
        m.no_pagado = True  # si tienes este campo para control
        m.save()

    print(f"✅ Membresías actualizadas automáticamente: {timezone.now()}")
