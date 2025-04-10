from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product

# Create your views here.

@csrf_exempt
def product_list(request):
    if request.method == 'GET':
        products = list(Product.objects.all())
        return JsonResponse(products, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        product = Product.objects.create(name=data['name'], price=data['price'])
        return JsonResponse({'id': product.id, 'name':product.name, 'price':product.price}, status=201)


def product_detail():