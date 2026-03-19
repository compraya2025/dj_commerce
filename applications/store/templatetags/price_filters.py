from django import template

register = template.Library()

@register.filter
def guarani(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", ".")
    except:
        return value


@register.filter
def multiply_by(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide_by(value, arg):
    """Divide el valor por el argumento"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value

@register.filter
def subtract(value, arg):
    """Resta el argumento del valor"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def apply_discount(price, discount_percentage):
    """Aplica un descuento porcentual al precio"""
    try:
        discount_amount = float(price) * float(discount_percentage) / 100
        return float(price) - discount_amount
    except (ValueError, TypeError):
        return price

@property
def final_price(self):
    return self.sale_price if self.promotion and self.sale_price else self.price
