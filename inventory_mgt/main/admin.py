from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Product, Location, Supplier, Inventory, Transaction, User

# Register your models here.
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Location)
admin.site.register(Supplier)
admin.site.register(Inventory)
admin.site.register(Transaction)