from django.contrib import admin

from .models import (
    Category,
    Product,
    Order,
    OrderItem,
)
from .google_sheets import update_order_in_google_sheet

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
        'stock',
        'is_new',
        'is_active',
        'created_at',
    )

    list_filter = (
        'category',
        'is_new',
        'is_active',
    )

    search_fields = (
        'name',
        'description',
    )

    list_editable = (
        'price',
        'stock',
        'is_new',
        'is_active',
    )

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        'product',
        'quantity',
        'price',
        'subtotal',
    )

    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'phone',
        'city',
        'total',
        'deposit',
        'payment_status',
        'created_at',
    )

    list_filter = (
        'payment_status',
        'created_at',
    )

    search_fields = (
        'name',
        'phone',
        'city',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        '-created_at',
    )

    inlines = [
        OrderItemInline,
    ]

    def save_model(self, request, obj, form, change):

        super().save_model(
            request,
            obj,
            form,
            change
        )

        try:

            update_order_in_google_sheet(obj)

        except Exception as e:

            print(
                "Google Sheets Update Error:",
                e
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
        'subtotal',
    )

    search_fields = (
        'order__name',
        'order__phone',
        'product__name',
    )