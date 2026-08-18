from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home , name='home'),
    path('shop/', views.shop , name='shop'),
    path(
        'products/add/',
        views.add_product,
        name='add_product'
    ),
    path(
        'products/manage/',
        views.manage_products,
        name='manage_products'
    ),
    path(
        'products/<int:product_id>/edit/',
        views.edit_product,
        name='edit_product'
    ),

    path(
        'products/<int:product_id>/delete/',
        views.delete_product,
        name='delete_product'
    ),
    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),
    path('about/', views.about , name='about'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart, name='cart'),
    path(
        'cart/update/<int:product_id>/',
        views.update_cart,
        name='update_cart'
    ),

    path(
        'cart/remove/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),
    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),
    path(
        'checkout/create/',
        views.create_order,
        name='create_order'
    ),
    path(
        'order-success/',
        views.order_success,
        name='order_success'
    ),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='store/login.html',
            next_page='/management/'
        ),
        name='login'
    ),

    path(
        'logout/',
        views.logout_user,
        name='logout'
    ),
    path(
        'products/manage/categories/',
        views.manage_categories,
        name='manage_categories'
    ),

    path(
        'products/manage/categories/add/',
        views.add_category,
        name='add_category'
    ),

    path(
        'products/manage/categories/<int:category_id>/edit/',
        views.edit_category,
        name='edit_category'
    ),

    path(
        'products/manage/categories/<int:category_id>/delete/',
        views.delete_category,
        name='delete_category'
    ),
    path(
        'products/manage/orders/',
        views.manage_orders,
        name='manage_orders'
    ),
    path(
        'products/manage/orders/<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),
    path(
        'products/manage/orders/<int:order_id>/status/',
        views.update_order_status,
        name='update_order_status'
    ),
    path(
        'orders/<int:order_id>/delete/',
        views.delete_order,
        name='delete_order'
    ),
    path(
        'management/',
        views.management_dashboard,
        name='management_dashboard'
    ),
]