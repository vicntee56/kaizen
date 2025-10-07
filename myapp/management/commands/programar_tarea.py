from django.core.management.base import BaseCommand
from background_task.models import Task
from myapp.tasks import actualizar_membresias

class Command(BaseCommand):
    help = "Programa la tarea de actualización automática de membresías"

    def handle(self, *args, **kwargs):
        # Eliminar tareas duplicadas para evitar que se acumulen
        Task.objects.filter(task_name="myapp.tasks.actualizar_membresias").delete()

        # Programar tarea cada 24 horas (86400 segundos)
        actualizar_membresias(repeat=60*60*24)  

        self.stdout.write(self.style.SUCCESS("✅ Tarea programada con éxito"))
