from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Wishlist, Order
from django.contrib.auth.models import User
from django.contrib import messages

def product_list(request):
    products = Product.objects.all()

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count() if request.user.is_authenticated else 0

    return render(request, 'store/product_list.html', {
        'products': products,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})

    if str(product.id) in cart:
        cart[str(product.id)] += 1
    else:
        cart[str(product.id)] = 1

    request.session['cart'] = cart

    messages.success(request, f"{product.name} added to cart 🛒")
    return redirect('product_list')


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total
        })
    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'store/cart.html', context)
@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('product_list')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items
    })

def increase_quantity(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        cart[str(id)] += 1
    request.session['cart'] = cart
    return redirect('cart')

def decrease_quantity(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        cart[str(id)] -= 1
        if cart[str(id)] <= 0:
            del cart[str(id)]
    request.session['cart'] = cart
    return redirect('cart')

def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        del cart[str(id)]
    request.session['cart'] = cart
    return redirect('cart')

#####Order placement
@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    total_price = 0
    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total_price += product.price * qty

    Order.objects.create(
        user=request.user,
        total_price=total_price
    )

    # Clear cart after order
    request.session['cart'] = {}

    return render(request, 'store/order_success.html', {
        'total_price': total_price
    })
##########MY ORDE?R???S

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required
def buy_now(request, id):
    product = get_object_or_404(Product, id=id)

    # Calculate total
    total_price = product.price

    # Create an order but mark it as unpaid
    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        status='Pending'  # make sure your Order model has a status field
    )
    order.products.add(product)
    # Optionally, store the product in the order if you have a ManyToManyField
    # order.products.add(product)

    messages.info(request, f"Proceeding to payment for {product.name}")
    return redirect('payment', order_id=order.id)


def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        # Fake payment success
        order.status = 'Paid'
        order.save()
        return redirect('order_success', order_id=order.id)

    return render(request, 'store/payment.html', {'order': order})

def order_success(request, order_id=None):
    order = None
    total_price = None

    if order_id:
        order = get_object_or_404(Order, id=order_id)
        total_price = order.total_price  # ← add this line
    else:
        # For cart checkout without order_id
        total_price = request.session.get('last_order_total', 0)

    return render(request, 'store/order_success.html', {
        'order': order,
        'total_price': total_price
    })
@login_required
def buy_now(request, id):
    product = get_object_or_404(Product, id=id)

    # Create order
    order = Order.objects.create(
        user=request.user,
        total_price=product.price,
        status="Pending"
    )

    order.products.add(product)

    messages.info(request, "Proceeding to payment")
    return redirect('payment', order_id=order.id)


@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        # Reduce stock
        for product in order.products.all():
            if product.stock > 0:
                product.stock -= 1
                product.save()

        order.status = 'Paid'
        order.save()

        return redirect('order_success', order_id=order.id)

    return render(request, 'store/payment.html', {'order': order})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {
        'order': order,
        'total_price': order.total_price
    })

