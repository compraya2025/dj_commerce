
from django.urls import path, include
from . import views

from applications.store.views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

urlpatterns = [
    # urls para resetear contraseña
    path('reset_password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset_password_send/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    #urls normal
    path('', views.home, name='home'),
    
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),

    path('update_password/', views.update_password, name='update_password'),
    path('update_info/', views.update_info, name='update_info'),
    path('update_user/', views.update_user, name='update_user'),
    
    path('products/<uuid:uid>', views.products, name='products'),
    path('search/', views.product_search, name='product_search'),
    path('category/<str:foo>', views.category, name='category'),

    #FAVORITOS
    path('favorite/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),
    
    path('favoritos/', views.my_favorites, name='my_favorites'),
    
]