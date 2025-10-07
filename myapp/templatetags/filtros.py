from django import template

register = template.Library()

@register.filter
def get_reserva(reservas_dict, clave):
    return reservas_dict.get(clave, 0)