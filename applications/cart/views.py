from django.shortcuts import render, get_object_or_404
from .cart import Cart
from django.contrib import messages
from applications.store.models import Product
from django.http import JsonResponse

import random

# Create your views here.
def cart(request):
    #OBTNER LOS PRODUCTOS
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    totals = cart.cart_total()

     # OBTENER PRODUCTOS RECOMENDADOS
    # Opción 1: Productos aleatorios excluyendo los del carrito
    cart_product_ids = [product.id for product in cart_products]

     # Obtener todos los productos disponibles
    all_products = Product.objects.all()
    
    # Excluir productos que ya están en el carrito
    available_products = all_products.exclude(id__in=cart_product_ids)
    
    # Tomar 4 productos aleatorios
    if available_products.count() >= 4:
        recommended_products = list(available_products.order_by('?')[:4])
    else:
        # Si no hay suficientes productos sin los del carrito, tomar algunos aleatorios
        recommended_products = list(all_products.order_by('?')[:4])
    
    # Opción 2: Productos de la misma categoría (si tu modelo tiene categorías)
    # Descomenta esto si quieres productos de la misma categoría

    # Si el carrito está vacío, mostrar productos populares
    if not cart_products:
        # Puedes cambiar esto para mostrar productos con más ventas, más vistos, etc.
        recommended_products = list(all_products.order_by('?')[:4])

    context = {
        'cart_products': cart_products,
        'quantities': quantities,
        'totals': totals,
        'recommended_products': recommended_products,  # Agregar esto
    }

    #return render(request, 'cart.html',{'cart_products':cart_products,'quantities':quantities, #'totals':totals})

    return render(request, 'cart.html', context)

def cart_add(request):
     cart = Cart(request)
     if request.POST.get('action') == 'post':
        # GET 
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # Mi rando la base de datos
        product = get_object_or_404(Product, id=product_id)
        # guarda la session
        cart.add(product=product, quantity=product_qty)
        
        # Obtencion cart cantidad
        cart_quantity = cart.__len__()
        
        response = JsonResponse({'qty: ': cart_quantity})  
        messages.success(request, ('Producto agregado en el carrito!!!'))      
        return response

def add(request):
    if request.method == "POST":
        try:
            cart = Cart(request)

            product_id = request.POST.get("product_id")
            product_qty = request.POST.get("product_qty")

            print("POST:", request.POST)  # DEBUG

            product = get_object_or_404(Product, id=product_id)

            cart.add(product=product, quantity=int(product_qty))

            return JsonResponse({
                "success": True,
                "qty": cart.__len__(),
                "product": product.title
            })

        except Exception as e:
            print("CART ERROR:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product_id)

        return JsonResponse({'product': product_id})
    
def cart_update(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = request.POST.get('product_qty')

        if not product_id or not product_qty:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        cart.update(
            product_id=int(product_id),
            quantity=int(product_qty)
        )

        total = cart.cart_total()

        return JsonResponse({
            'qty': product_qty,
            'total': total
        })
