from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Category, Customer, Product, Order, Profile, OrderAudit, Favorite

from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
# Register your models here.


""" #Mix profile info and user info
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")

    search_fields = ("username", "first_name", "last_name", "email")

    ordering = ("username",)
    field = ['username','first_name', 'last_name', 'email']
    inlines = [ProfileInline]



admin.site.unregister(User)

admin.site.register(User, UserAdmin)
"""
admin.site.register(Profile)
 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','created_at','updated_at')

    search_fields = ('id','name')

    list_per_page = 10  

    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')

    list_per_page = 10 

class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Product
        fields = '__all__'

    def clean_sale_price(self):
        price = self.cleaned_data.get('price')
        sale_price = self.cleaned_data.get('sale_price')
        if sale_price and sale_price > price:
            raise forms.ValidationError("El precio de oferta no puede ser mayor que el precio normal.")
        return sale_price


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title','brand', 'price', 'stock', 'promotion', 'category')
    search_fields = ('title', 'brand', 'sku', 'category__name')
    list_filter = ('promotion', 'category', 'created')

    list_per_page = 10 
    ordering = ('-created',)

    fieldsets = (
        (None, {
            'fields': ('title', 'brand', 'sku', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'sale_price', 'stock', 'promotion')
        }),
        ('Product Details', {
            'fields': ('material_product', 'color', 'garantia_product')
        }),
        ('Images', {
            'fields': ('url_image_one_product', 'url_image_two_product', 'url_image_three_product')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created', 'modified')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'customer', 'quantity', 'status', 'created')
    list_filter = ('status',)


@admin.register(OrderAudit)
class OrderAuditAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'title',
        'price',
        'quantity',
        'address',
        'phone',
        'action',
        'created_at'
    )
    list_filter = ('action', 'created_at')
    search_fields = ('title', 'address', 'phone')
    ordering = ('-created_at',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__title')
    list_filter = ('created_at',)