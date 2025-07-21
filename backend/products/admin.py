from django.contrib import admin
from .models import ProductCategory, Product, ProductListing

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'parent_category', 'is_active', 'products_count')
    list_filter = ('is_active', 'parent_category')
    search_fields = ('category_name', 'description')
    ordering = ('category_name',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products')

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'No. of Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'unit_of_measure', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_perishable', 'category')
    search_fields = ('product_name', 'description')
    ordering = ('-created_at',)

@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = ('product', 'farmer', 'farm', 'current_price', 'quantity_available', 'listing_status', 'created_at')
    list_filter = ('listing_status', 'quality_grade', 'is_organic_certified', 'farm')
    search_fields = ('product__product_name', 'farmer__username', 'farm__farm_name')
    ordering = ('-created_at',)
    raw_id_fields = ('farmer', 'farm', 'product')
