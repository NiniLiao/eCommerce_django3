from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from .lineapi import *


# Create your views here.

def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all
    context = { 'products':products, 'cartItems':cartItems }
    return render(request, 'store/store.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}   
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)

    # total = float(data['form']['total'])
    total = 100
    
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
        order.save()

    if order.shipping != 'True':
        ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
    )    


    payProvider = LinePayApi('1655386484', 'e0fd66b6163bde8335040cfc28062399', True)
    options = {
        'amount': total,
        'currency': 'TWD',
        'orderId': transaction_id,
        'packages': [
            { 
                'id': 1,
                'amount': total,
                'name': 'fake package',
                'products': [
                    {
                        'name': 'fake product',
                        'quantity': '1',
                        'price': total,
                    }
                ]
            }
        ],
        'redirectUrls': {
            'confirmUrl': 'http://127.0.0.1:8000/',
            'cancelUrl': 'http://127.0.0.1:8000/',
        }
    }
    result = payProvider.request(options)
    weburl = result.get('info').get('paymentUrl').get('web')
    
    return JsonResponse({'message': 'Payment complete! ', 'payLink': weburl}, safe=False)
