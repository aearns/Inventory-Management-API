from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token



# Create your models here.
class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank= True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
   
    def __str__(self):
        return f"{self.name} (SKU): {self.sku}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'main_user'
        
# Automatically create auth token when user is created
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    
#Track inventory storage
class Location(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(blank=True)
    is_warehouse = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
#stock levels
class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together =('product', 'location')

    def __str__(self):
        return f"{self.product.name} at {self.location.name}:{self.quantity}"

#supplier deets for restocking   
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, blank=True)

    def __str__(self):
        return self.name

#stock movements 
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase from Supplier'),
        ('SALE', 'Sale to Customer'),
        ('TRANSFER', 'Transfer between Locations'),
        ('ADJUSTMENT', 'Manual Adjustment'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    location_from = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_out')
    location_to = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_in')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.product.name} ({self.quantity})"
