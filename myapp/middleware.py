from .models import Visita
from .utils import get_geo_from_ip

class VerificacionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Aquí va la lógica de verificación
        # Si deseas que la verificación no interfiera con el flujo, solo imprime algo en consola
        print("Verificación activada")
        
        response = self.get_response(request)
        return response
    

class RegistrarVisitasMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_staff:
            ip = request.META.get('REMOTE_ADDR', '')
            geo = get_geo_from_ip(ip)
            Visita.objects.create(ip=ip, ciudad=geo['ciudad'], region=geo['region'])
        return self.get_response(request)