from django.shortcuts import render , get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from decimal import Decimal
from django.contrib import messages
from urllib.parse import quote
from .models import Product, Category, Order, OrderItem
from .google_sheets import (
    add_order_to_google_sheet,
    update_order_in_google_sheet,
)
# Create your views here.
def home(request):
    return render(request, 'store/home.html')

def shop(request):

    products = Product.objects.filter(
        is_active=True
    ).select_related('category')

    categories = Category.objects.all()

    selected_category = request.GET.get('category')
    sort = request.GET.get('sort')

    # Filter by category
    if selected_category:
        products = products.filter(
            category__slug=selected_category
        )

    # Sort products
    if sort == 'newest':
        products = products.order_by('-created_at')

    elif sort == 'price_low':
        products = products.order_by('price')

    elif sort == 'price_high':
        products = products.order_by('-price')

    else:
        products = products.order_by('-created_at')

    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_sort': sort,
    })

def about(request):
    return render(request, 'store/about.html')

def contact(request):
    return render(request, 'store/contact.html')

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('shop')

def cart(request):

    cart_data = request.session.get('cart', {})

    products = []

    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        subtotal = product.price * quantity

        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

        total += subtotal

    return render(request, 'store/cart.html', {
        'cart_items': products,
        'total': total,
    })

def update_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:

        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart[product_id] = quantity
        else:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def remove_from_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

def checkout(request):

    cart_data = request.session.get('cart', {})

    if not cart_data:
        return redirect('cart')

    cart_items = []
    total = Decimal('0.00')

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        subtotal = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

        total += subtotal

    deposit = total / Decimal('2')

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'deposit': deposit,
    })


def create_order(request):

    if request.method != 'POST':
        return redirect('checkout')

    # =========================
    # GET CART
    # =========================

    cart_data = request.session.get('cart', {})

    if not cart_data:
        return redirect('cart')


    # =========================
    # CUSTOMER DATA
    # =========================

    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    city = request.POST.get('city', '').strip()
    address = request.POST.get('address', '').strip()
    notes = request.POST.get('notes', '').strip()

    deposit_confirmed = request.POST.get(
        'deposit_confirmed'
    )


    # =========================
    # VALIDATION
    # =========================

    if not name or not phone or not city or not address:

        messages.error(
            request,
            'Please fill in all required fields.'
        )

        return redirect('checkout')


    if not deposit_confirmed:

        messages.error(
            request,
            'Please confirm that you have transferred the deposit.'
        )

        return redirect('checkout')


    # =========================
    # CALCULATE ORDER
    # =========================

    total = Decimal('0.00')

    order_products = []


    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        quantity = int(quantity)

        if quantity <= 0:
            continue


        subtotal = product.price * quantity

        total += subtotal


        order_products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })


    if not order_products:

        return redirect('cart')


    # =========================
    # DEPOSIT = 50%
    # =========================

    deposit = total / Decimal('2')


    # =========================
    # CREATE ORDER
    # =========================

    order = Order.objects.create(

        name=name,

        phone=phone,

        city=city,

        address=address,

        notes=notes,

        total=total,

        deposit=deposit,

        payment_status='deposit_paid'

    )


    # =========================
    # CREATE ORDER ITEMS
    # =========================

    for item in order_products:

        OrderItem.objects.create(

            order=order,

            product=item['product'],

            quantity=item['quantity'],

            price=item['product'].price,

            subtotal=item['subtotal']

        )
       # Add order to Google Sheets

    try:
        add_order_to_google_sheet(order)
    except Exception as e:
        print("Google Sheets Error:", e)

    # =========================
    # SAVE LAST ORDER
    # =========================

    request.session['last_order_id'] = order.id


    # =========================
    # CLEAR CART
    # =========================

    request.session['cart'] = {}

    request.session.modified = True


    # =========================
    # SUCCESS PAGE
    # =========================

    return redirect('order_success')


def order_success(request):

    order_id = request.session.get('last_order_id')

    if not order_id:
        return redirect('shop')

    order = get_object_or_404(
        Order,
        id=order_id
    )

    message = "Hello Planet Accessories,\n\n"

    message += f"I have placed Order #{order.id}.\n\n"

    message += f"Customer: {order.name}\n"
    message += f"Phone: {order.phone}\n"
    message += f"City: {order.city}\n"
    message += f"Address: {order.address}\n\n"

    # =========================
    # PRODUCTS
    # =========================

    message += "Products:\n\n"

    for item in order.items.all():

        if item.product.image:

            image_url = request.build_absolute_uri(
                item.product.image.url
            )

            message += (
                f"📷 Product Image:\n"
                f"{image_url}\n"
                f"Quantity: {item.quantity}\n"
                f"Subtotal: ${item.subtotal}\n\n"
            )

        else:

            message += (
                f"Product: {item.product.name}\n"
                f"Quantity: {item.quantity}\n"
                f"Subtotal: ${item.subtotal}\n\n"
            )

    message += f"Total: ${order.total}\n"
    message += f"50% Deposit: ${order.deposit}\n"
    message += "Deposit Status: Paid"

    if order.notes:
        message += f"\n\nOrder Notes: {order.notes}"

    whatsapp_number = "201154924126"

    whatsapp_url = (
        f"https://wa.me/{whatsapp_number}"
        f"?text={quote(message)}"
    )

    return render(
        request,
        'store/order_success.html',
        {
            'order': order,
            'whatsapp_url': whatsapp_url,
        }
    )

@login_required
def add_product(request):

    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        is_new = request.POST.get('is_new') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')

        category = get_object_or_404(
            Category,
            id=category_id
        )

        Product.objects.create(
            category=category,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image,
            is_new=is_new,
            is_active=is_active
        )

        return redirect('manage_products')

    return render(
        request,
        'store/add_product.html',
        {
            'categories': categories
        }
    )

@login_required
def management_dashboard(request):

    products_count = Product.objects.count()
    categories_count = Category.objects.count()
    orders_count = Order.objects.count()

    pending_orders = Order.objects.filter(
        payment_status='pending'
    ).count()

    deposit_paid_orders = Order.objects.filter(
        payment_status='deposit_paid'
    ).count()

    confirmed_orders = Order.objects.filter(
        payment_status='confirmed'
    ).count()

    return render(
        request,
        'store/management_dashboard.html',
        {
            'products_count': products_count,
            'categories_count': categories_count,
            'orders_count': orders_count,
            'pending_orders': pending_orders,
            'deposit_paid_orders': deposit_paid_orders,
            'confirmed_orders': confirmed_orders,
        }
    )


@login_required
def manage_products(request):

    products = Product.objects.select_related(
        'category'
    ).order_by('-created_at')

    return render(
        request,
        'store/manage_products.html',
        {
            'products': products
        }
    )

@login_required
def edit_product(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':

        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')

        category_id = request.POST.get('category')

        product.category = get_object_or_404(
            Category,
            id=category_id
        )

        product.is_new = request.POST.get('is_new') == 'on'
        product.is_active = request.POST.get('is_active') == 'on'

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        return redirect('manage_products')

    return render(
        request,
        'store/edit_product.html',
        {
            'product': product,
            'categories': categories
        }
    )


@login_required
def delete_product(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':
        product.delete()

    return redirect('manage_products')

@login_required
def manage_categories(request):
    categories = Category.objects.all().order_by('name')

    return render(
        request,
        'store/manage_categories.html',
        {
            'categories': categories
        }
    )


@login_required
def add_category(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        slug = request.POST.get('slug')

        if name and slug:

            Category.objects.create(
                name=name,
                slug=slug
            )

            return redirect('manage_categories')

    return render(
        request,
        'store/add_category.html'
    )


@login_required
def edit_category(request, category_id):

    category = get_object_or_404(
        Category,
        id=category_id
    )

    if request.method == 'POST':

        name = request.POST.get('name')
        slug = request.POST.get('slug')

        if name and slug:

            category.name = name
            category.slug = slug

            category.save()

            return redirect('manage_categories')

    return render(
        request,
        'store/edit_category.html',
        {
            'category': category
        }
    )


@login_required
def delete_category(request, category_id):

    category = get_object_or_404(
        Category,
        id=category_id
    )

    if request.method == 'POST':

        category.delete()

        return redirect('manage_categories')

    return render(
        request,
        'store/delete_category.html',
        {
            'category': category
        }
    )

@login_required
def manage_orders(request):

    orders = Order.objects.all().order_by('-created_at')

    return render(
        request,
        'store/manage_orders.html',
        {
            'orders': orders
        }
    )

@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    phone = order.phone.strip()

    if phone.startswith('0'):
        whatsapp_phone = '20' + phone[1:]
    elif phone.startswith('20'):
        whatsapp_phone = phone
    else:
        whatsapp_phone = phone

    whatsapp_message = (
        f"Hello {order.name}, "
        f"this is Planet Accessories regarding "
        f"Order #{order.id}."
    )

    whatsapp_url = (
        f"https://wa.me/{whatsapp_phone}"
        f"?text={quote(whatsapp_message)}"
    )

    return render(
        request,
        'store/order_detail.html',
        {
            'order': order,
            'whatsapp_url': whatsapp_url,
        }
    )

@login_required
def update_order_status(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == 'POST':

        new_status = request.POST.get('payment_status')

        valid_statuses = [
            'pending',
            'deposit_paid',
            'confirmed',
            'cancelled',
        ]

        if new_status not in valid_statuses:

            messages.error(
                request,
                'Invalid order status.'
            )

            return redirect(
                'order_detail',
                order_id=order.id
            )

        # =========================
        # UPDATE DATABASE
        # =========================

        order.payment_status = new_status

        order.save()

        # =========================
        # UPDATE GOOGLE SHEET
        # =========================

        try:

            update_order_in_google_sheet(order)

            messages.success(
                request,
                f'Order #{order.id} updated successfully.'
            )

        except Exception as e:

            print(
                "Google Sheets Update Error:",
                e
            )

            messages.warning(
                request,
                'Order updated successfully, but Google Sheet could not be updated.'
            )

        return redirect(
            'order_detail',
            order_id=order.id
        )

    return redirect(
        'order_detail',
        order_id=order.id
    )

@login_required
def delete_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == 'POST':

        order.delete()

        messages.success(
            request,
            f'Order #{order_id} deleted successfully.'
        )

        return redirect('manage_orders')

    return redirect(
        'order_detail',
        order_id=order.id
    )

def logout_user(request):

    logout(request)

    return redirect('home')