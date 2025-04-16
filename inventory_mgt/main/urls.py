from django.urls import path
from . import views
from .views import login_user, logout_user, register_user, add_inventory

urlpatterns = [

    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    path('products/add/', views.add_product, name='add-product'),    # POST
    path('products/view/', views.view_products, name='view-product'),    # This is a GET request
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),     # GET specific request
    
    path('inventory/add/', add_inventory),
    path('locations/add/', views.add_location),
    path('suppliers/add/', views.add_supplier),
    path('inventory/add/', views.add_inventory),
    path('transactions/add/', views.add_transaction),
    
    path('locations/', views.get_locations),
    path('suppliers/', views.get_suppliers),
    path('inventory/', views.get_inventory),
    path('transactions/', views.get_transactions),
   
]