from django.contrib import admin
from .models import Category, Product, Order, OrderItem, ContactMessage, Review


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "qty", "unit_price", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Table-la theriyura columns
    list_display = ("order_id", "name", "status", "payment_method", "total", "created_at")
    
    # Intha oru line thaan mukkiyam: Table list-laye direct-ah dropdown vechu status maathikkalaam
    list_editable = ("status",)
    
    # Filter & Search
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order_id", "name", "address", "city")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone", "message")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 'stock' remove panniyaachu
    list_display = ("name", "category", "price", "is_featured", "is_back_to_school")
    list_filter = ("category", "is_featured", "is_back_to_school")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating")
    list_filter = ("rating",)