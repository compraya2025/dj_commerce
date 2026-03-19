from .cart import Cart

# CREA UN PROCESO DE CONTEXT PARA EL CARRITO FUNCIONA EN TODA LA PÁGINA DEL SITIO WEB
def cart(request):
    return {'cart': Cart(request)}