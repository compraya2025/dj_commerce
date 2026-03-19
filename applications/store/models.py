from django.db import models
import datetime
import uuid
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from ckeditor.fields import RichTextField

from django.db import transaction
from django.core.exceptions import ValidationError
User = get_user_model() 

#Crear perfil
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    addres1 = models.CharField(max_length=200, blank=True)
    addres2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'profiles'
        verbose_name_plural = 'profiles'
    def __str__(self):
        return self.user.username

# Crear un perfil de usuario de forma predeterminada cuando el usuario se registra
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

# Automatizar la creación de perfiles
post_save.connect(create_profile, sender=User)

# Categoria
class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'


# Cliente
class Customer(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'customers'
        verbose_name_plural = 'customers'


# Producto
class Product(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True )
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=150, blank=True)
    description = RichTextField(null=True, blank=True)
    sku = models.CharField(max_length=150, unique=True)
    stock = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    promotion = models.BooleanField(default=False)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    url_image_one_product = models.ImageField(upload_to='product/', blank=True)
    url_image_two_product = models.ImageField(upload_to='product/', blank=True)
    url_image_three_product = models.ImageField(upload_to='product/', blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    material_product = models.CharField(max_length=60, null=True)
    color = models.CharField(max_length=60, null=True)
    garantia_product = models.CharField(max_length=80, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'products'
        verbose_name_plural = 'products'
    
    @property
    def final_price(self):
        return self.sale_price if self.promotion and self.sale_price else self.price

    def is_favorite(self, user):
        if user.is_authenticated:
            return self.favorited_by.filter(user=user).exists()
        return False


# Pedido
class Order(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.date.today)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    #def save(self, *args, **kwargs):
        # Solo descontar si es nuevo pedido
       # if not self.pk:
            #if self.product.stock < self.quantity:
                #raise ValidationError("No hay suficiente stock disponible")

            #with transaction.atomic():
                #self.product.stock -= self.quantity
                #self.product.save()

        #super().save(*args, **kwargs)


    def save(self, *args, **kwargs):

      
        is_new = self.pk is None
        action = None

        with transaction.atomic():

            if is_new:
                if self.product.stock < self.quantity:
                    raise ValidationError("No hay suficiente stock disponible")

                self.product.stock -= self.quantity
                self.product.save()

                action = "CREATED"

            else:
                old_order = Order.objects.select_for_update().get(pk=self.pk)

                # Si cambia producto
                if old_order.product != self.product:
                    old_order.product.stock += old_order.quantity
                    old_order.product.save()

                    if self.product.stock < self.quantity:
                        raise ValidationError("No hay suficiente stock disponible")

                    self.product.stock -= self.quantity
                    self.product.save()

                    action = "PROCESS"

                # Si cambia cantidad
                elif old_order.quantity != self.quantity:
                    difference = self.quantity - old_order.quantity

                    if difference > 0:
                        if self.product.stock < difference:
                            raise ValidationError("No hay suficiente stock disponible")
                        self.product.stock -= difference
                    else:
                        self.product.stock += abs(difference)

                    self.product.save()
                    action = "PROCESS"

                # Si cambia estado
                if not old_order.status and self.status:
                    action = "COMPLETED"

            super().save(*args, **kwargs)

            if action:
                OrderAudit.objects.create(
                    product=self.product,
                    user=self.user if hasattr(self, 'user') else None,
                    title=self.product.title,
                    price=self.product.final_price,
                    quantity=self.quantity,
                    address=self.address,
                    phone=self.phone,
                    action=action
                )


    def __str__(self):
        return f"Order #{self.id}"

    class Meta:
        db_table = 'orders'
        verbose_name_plural = 'orders'

class OrderAudit(models.Model):

    ACTION_CHOICES = (
        ('CREATED', 'Created'),
        ('PROCESS', 'Process'),
        ('COMPLETED', 'Completed'),
        ('DELETED', 'Deleted'),
    )
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.action}"

    class Meta:
        db_table = 'order_audit'
        verbose_name_plural = 'Order Audit'
        ordering = ['-created_at']

# Favoritos
class Favorite(models.Model):
   
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        verbose_name_plural = 'favorites'
        unique_together = ('user', 'product')  # Evita duplicados

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.title}"
