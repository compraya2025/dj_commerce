from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

#@register.filter
#def get_item(dictionary, key):
#    return dictionary.get(str(key))

@register.filter
def get_item(dictionary, key):
    """Obtiene un valor de un diccionario por clave"""
    try:
        # Si es un diccionario
        if hasattr(dictionary, 'get'):
            # Convertir key a string si es necesario
            if isinstance(key, (int, float)):
                key = str(key)
            return dictionary.get(key)
        # Si no es diccionario, retornar el valor por defecto
        return dictionary
    except (AttributeError, TypeError):
        # Si hay error, retornar 1 como cantidad por defecto
        return 1

@register.filter
def subtract(value, arg):
    """Resta arg de value"""
    try:
        result = float(value) - float(arg)
        return result if result > 0 else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def calculate_subtotal(price, quantity):
    """Calcula el subtotal (precio * cantidad)"""
    try:
        return float(price) * float(quantity)
    except (ValueError, TypeError):
        return 0