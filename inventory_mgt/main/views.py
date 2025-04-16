import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
from rest_framework.authtoken.models import Token

from .models import Product, Location, Inventory, Supplier, Transaction


# Create your views here.

@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = Product.objects.create(sku=data["sku"], name=data["name"], quantity=data["quantity"], 
                                         price=data["price"], category=data["category"], unit_cost=data["unit_cost"])
        return JsonResponse({"id": product.id, "sku":product.sku, "name":product.name, "price":product.price,
                             "quantity":product.quantity, "category":product.category}, status=201)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405) 


@csrf_exempt
def view_products(request):
    if request.method == 'GET':
        products = Product.objects.all()
        json_data= serializers.serialize('json', products)
        json_data = json.loads(json_data)
        return JsonResponse({"products":json_data}, status=200, safe=False)
    else:
        return JsonResponse({"error": "Request not allowed"}, status=405) 


@csrf_exempt
def product_detail(request, product_id):
    # try:
    #     data = Product.objects.filter(pk=product_id).first()
    #     json_data = serializers.serialize('json', [data]) 
    #     json_data = json.loads(json_data)

    #     return JsonResponse({"data": json_data}, status=200)
    
    # except Product.DoesNotExist:
    #     return JsonResponse({'error': 'Product not found'}, status = 404)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'id': product.id, 'name': product.name, 'price': product.price})

    elif request.method == 'PUT':
        data = json.loads(request.body)
        product.name = data['name']
        product.price = data['price']
        product.quantity = data['quantity']
        product.save()
        return JsonResponse({'id': product.id, 'name': product.name, 'price': product.price}) 

    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse({'message': 'Product deleted'})


User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['username', 'password', 'email']
        if not all(k in data for k in required_fields):
            return JsonResponse({'error': f'Missing required fields: {required_fields}'}, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            #phone=data.get('phone', '')
        )
        
        return JsonResponse({
            'message': 'User registered successfully',
            'user_id': user.id,
            'username': user.username
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        
        if not all(k in data for k in ['username', 'password']):
            return JsonResponse({'error': 'Missing username or password'}, status=400)
            
        user = authenticate(username=data['username'], 
                            password=data['password'])
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'token': token.key
            })
            
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def logout_user(request):
    try:
        # Get token from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
        
        if len(auth_header) == 2 and auth_header[0].lower() == 'token':
            try:
                token = Token.objects.get(key=auth_header[1])
                token.delete()
                logout(request)
                return JsonResponse({'message': 'Logout successful'})
            except Token.DoesNotExist:
                pass
                
        return JsonResponse({'error': 'Invalid token'}, status=401)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def add_inventory(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        inventory, created = Inventory.objects.update_or_create(
            product_id=data['product_id'],
            location_id=data['location_id'],
            defaults={'quantity': data['quantity']}
        )
        return JsonResponse({
            'message': 'Inventory created' if created else 'Inventory updated',
            'id': inventory.id
        })

@csrf_exempt
def add_supplier(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        supplier = Supplier.objects.create(
            name=data['name'],
            contact_person=data.get('contact_person', ''),
            phone=data['phone'],
            email=data.get('email', '')
        )
        return JsonResponse({'message': 'Supplier added', 'id': supplier.id})
    

@csrf_exempt
def add_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        location = Location.objects.create(
            name=data['name'],
            address=data.get('address', ''),
            is_warehouse=data.get('is_warehouse', False)
        )
        return JsonResponse({'message': 'Location added', 'id': location.id})

@csrf_exempt
def add_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        product_id = data["product_id"]
        qty = data['quantity']
        trans_type = data['transaction_type']
        loc_from = data.get('location_from_id')
        loc_to = data.get('location_to_id')

        # Create transaction log
        transaction = Transaction.objects.create(
            product_id=product_id,
            quantity=qty,
            transaction_type=trans_type,
            location_from_id=loc_from,
            location_to_id=loc_to,
            supplier_id=data.get('supplier_id'),
            notes=data.get('notes', '')
        )

        if trans_type == 'PURCHASE':
            Inventory.objects.update_or_create(
                product_id=product_id,
                location_id=loc_to,
                defaults={'quantity': models.F('quantity') + qty}
            )

        elif trans_type == 'SALE':
            Inventory.objects.update_or_create(
                product_id=product_id,
                location_id=loc_from,
                defaults={'quantity': models.F('quantity') - qty}
            )

        elif trans_type == 'TRANSFER':
            # Subtract from source
            Inventory.objects.update_or_create(
                product_id=product_id,
                location_id=loc_from,
                defaults={'quantity': models.F('quantity') - qty}
            )

         # Add to destination
            Inventory.objects.update_or_create(
                product_id=product_id,
                location_id=loc_to,
                defaults={'quantity': models.F('quantity') + qty}
            )

        elif trans_type == 'ADJUSTMENT':
            Inventory.objects.update_or_create(
                product_id=product_id,
                location_id=loc_to or loc_from,
                defaults={'quantity': qty}
            )

        return JsonResponse({'message': 'Transaction recorded and inventory updated'})


@csrf_exempt
def get_locations(request):
    locations = list(Location.objects.values())
    return JsonResponse(locations, safe=False)


@csrf_exempt
def get_suppliers(request):
    suppliers = list(Supplier.objects.values())
    return JsonResponse(suppliers, safe=False)


@csrf_exempt
def get_inventory(request):
    product_id = request.GET.get('product_id')
    location_id = request.GET.get('location_id')

    filters = {}
    if product_id:
        filters['product_id'] = product_id
    if location_id:
        filters['location_id'] = location_id

    inventory = list(Inventory.objects.filter(**filters).values())
    return JsonResponse(inventory, safe=False)


@csrf_exempt
def get_transactions(request):
    product_id = request.GET.get('product_id')
    filters = {'product_id': product_id} if product_id else {}
    transactions = list(Transaction.objects.filter(**filters).values())
    return JsonResponse(transactions, safe=False)
