from django import template

register = template.Library()

@register.filter
def get_horario_por_dia(horarios, dia):
    for horario in horarios:
        if horario.dia.lower() == dia.lower():
            return horario
    return None
