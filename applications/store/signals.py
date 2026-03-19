from django.db.models.signals import post_save
from django.dispatch import receiver 
from .models import Order

@receiver(post_save, sender=Order)
def update_stock_after_order(sender, instance, created, **kwargs):
    if created:
        product = instance.product

        # Validar stock disponible
        if product.stock >= instance.quantity:
            product.stock -= instance.quantity
            product.save()
        else:
            raise ValueError("Stock insuficiente para completar la orden")