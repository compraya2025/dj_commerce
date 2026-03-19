
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse

from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Customer, Product, Order, Profile, Favorite

from django.db.models import Q
from django import forms
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm

import json
from applications.cart.cart import Cart

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


# Vista para solicitar reset de contraseña
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = "autenticacion/password_reset.html"
    email_template_name = "autenticacion/password_reset_email.html"
    success_url = reverse_lazy('password_reset_done')


# Mensaje cuando el email fue enviado
class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "autenticacion/password-reset-sent.html"


# Vista donde el usuario escribe la nueva contraseña
class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "autenticacion/password-confirm.html"
    success_url = reverse_lazy('password_reset_complete')


# Vista final
class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "autenticacion/password-reset-complete.html"


def some_view(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        # otros datos para tu template
    }
    return render(request, 'helper/navbar.html', context)


def product_search(request):
    query = request.GET.get('q', '')

    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    ) if query else Product.objects.none()

    return render(request, 'search_results.html', {
        'products': products,
        'query': query
    })


def products(request,uid):
    products = Product.objects.get(uid=uid)
    recommended_products = Product.objects.filter(category=products.category).exclude(id=products.id)[:4]
    return render(request, 'product.html', {'products':products,  'recommended_products': recommended_products})

def home(request):
    products = Product.objects.all()
    promo_products = Product.objects.filter(promotion=True)
    categories = Category.objects.all()
    return render(request, 'home.html', {'products':products,'promo_products': promo_products, 'categories':categories})

def category(request,foo):
     # Convertir foo de slug a nombre normal (reemplazar guiones por espacios)
    category_name = foo.replace('-', ' ')
    
    category = get_object_or_404(Category, name__iexact=category_name)
    products = Product.objects.filter(category=category)

    return render(request, 'category.html', {
        'category': category,
        'products': products
    })


@login_required
def update_info(request):
    current_user, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserInfoForm(request.POST, instance=current_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información actualizada correctamente')
            return redirect('home')
    else:
        form = UserInfoForm(instance=current_user)

    return render(request, 'update_info.html', 
    {
        'form': form
    })
           

@login_required
def update_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            messages.success(request, 'Contraseña actualizada correctamente')
            return redirect('login')
        else:
            messages.error(request, '❌ Revisa los datos del formulario')
    else:
        form =  ChangePasswordForm(request.user) 

    return render(request,'update_password.html', {'form':form})

@login_required
def update_user(request):
    current_user = request.user

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('home')
    else:
        user_form = UpdateUserForm(instance=current_user)

    return render(request, 'update_user.html', {
        'user_form': user_form
    })

@login_required
def update_user(request):
    current_user = request.user

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('home')
    else:
        user_form = UpdateUserForm(instance=current_user)

    return render(request, 'update_user.html', {
        'user_form': user_form
    })

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            current_user, created = Profile.objects.get_or_create(user=request.user)
            saved_cart = current_user.old_cart
          
            cart = Cart(request)

            if saved_cart:
              #convertir en diccionario a json
              converted_cart = json.loads(saved_cart)
              #agregar la recarga de cart en diccionario 
              cart = Cart(request)

              for key, value in converted_cart.items():
                 cart.db_add(product=key, quantity=value)

            messages.success(request, f'¡Bienvenido {username}! Has iniciado sesión correctamente.')
            
            # Redirigir a la página anterior o a home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos')
    
    # Si es GET o si falló el login, mostrar el formulario
    return render(request, 'login.html')

def logout_user(request):
   logout(request)
   messages.success(request,'HAS SALIDO DE LA SECCION DE INICIO!')
   return redirect('home')  

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'✅ Usuario {username} registrado y logueado correctamente.')
            return redirect('home')
        else:
            print(form.errors)
            messages.error(request, '❌ Revisa los campos, hay errores en el formulario.')
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form':form})

#Favorito
#@login_required
def toggle_favorite(request):

    if request.method == 'POST':

        product_id = request.POST.get('product_id')
        print(product_id)

        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'No product id'}, status=400)

        product = get_object_or_404(Product, id=product_id)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            favorite.delete()
            return JsonResponse({'status': 'removed'})

        return JsonResponse({'status': 'added'})

    return JsonResponse({'status': 'invalid_request'}, status=400)

def product_detail(request, id):
    product = Product.objects.get(id=id)

    is_favorite = False

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            product=product
        ).exists()

    context = {
        'products': product,
        'is_favorite': is_favorite
    }

    return render(request, 'product_detail.html', context)

@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)

    context = {
        'favorites': favorites
    }

    return render(request, 'favorites.html', context)



