from .models import CartItem, Product
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib import messages
from django.shortcuts import redirect



def _cart_id(request):
    if 'cart_id' not in request.session:
        request.session['cart_id'] = _generate_cart_id()

    return request.session['cart_id']


def _generate_cart_id():
    import string, random
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(50)])


def get_all_cart_items(request):
    return CartItem.objects.filter(cart_id = _cart_id(request))


def add_item_to_cart(request):
    # cart_id = _cart_id(request)

    product_id = request.form_data['product_id']
    quantity = request.form_data['quantity']

    p = get_object_or_404(Product, id=product_id)

    price = p.price

    cart_items = get_all_cart_items(request)

    item_in_cart = False

    for cart_items in cart_items:
        if cart_items.product_id == product_id:
            cart_items.update_quantity(quantity)
            # cart_items.save()
            item_in_cart = True

    if not item_in_cart:
        item = CartItem(
            cart_id = _cart_id(request),
            price = price,
            quantity = quantity,
            product_id = product_id,
        )

        # item.cart_id = cart_id
        item.save()


def item_count(request):
    return get_all_cart_items(request).count()


def subtotal(request):
    cart_items = get_all_cart_items(request)
    sub_total = 0
    for item in cart_items:
        sub_total += item.total_cost()

    return sub_total


def remove_item(request):
    item_id = request.POST.get('item_id')
    ci = get_object_or_404(CartItem, id=item_id)
    ci.delete()


def update_item(request):
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')
    ci = get_object_or_404(CartItem, id=item_id)
    product = Product.objects.get(id=ci.product_id)
    if int(quantity) > product.products_count:
        messages.error(request, f'Only {product.products_count} of {product.name} products available.')
        return redirect('show_cart')
    else:
        product.products_count -= int(quantity)
        product.save()
        ci.quantity = quantity
        ci.save()



def clear(request):
    cart_items = get_all_cart_items(request)
    cart_items.delete()