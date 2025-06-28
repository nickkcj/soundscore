from django import template

register = template.Library()

@register.filter
def ms_to_mmss(value):
    try:
        value = int(value)
        minutes = value // 60000
        seconds = (value % 60000) // 1000
        return f"{minutes}:{seconds:02d}"
    except Exception:
        return ""