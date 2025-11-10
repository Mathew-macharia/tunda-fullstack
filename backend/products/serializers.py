from rest_framework import serializers
from django.utils import timezone
from django.db.models import Avg, Count
from .models import ProductCategory, Product, ProductListing
from farms.models import Farm
from feedback.models import Review # Import the Review model

class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for the ProductCategory model"""
    children_count = serializers.SerializerMethodField(read_only=True)
    products_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = [
            'category_id', 'parent_category', 'category_name', 
            'description', 'is_active', 'children_count', 'products_count'
        ]
        read_only_fields = ['category_id']
    
    def get_children_count(self, obj):
        """Get the count of child categories"""
        return obj.children.count()
    
    def get_products_count(self, obj):
        """Get the count of products in this category"""
        return obj.products.count()
    
    def to_representation(self, instance):
        """Add parent category name to the representation"""
        representation = super().to_representation(instance)
        if instance.parent_category:
            representation['parent_category_name'] = instance.parent_category.category_name
        return representation

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model"""
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_of_measure_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'product_id', 'category', 'category_name', 'product_name', 
            'description', 'unit_of_measure', 'unit_display', 'is_perishable', 
            'shelf_life_days', 'image_url', 'is_active', 'created_at'
        ]
        read_only_fields = ['product_id', 'created_at']
    
    def validate_category(self, value):
        """Ensure the category is active"""
        if not value.is_active:
            raise serializers.ValidationError("Cannot assign product to an inactive category.")
        return value

class ProductListingSerializer(serializers.ModelSerializer):
    """Serializer for the ProductListing model"""
    farmer_name = serializers.SerializerMethodField(read_only=True)
    farm_name = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all()) # Allow product_id as input
    product_name = serializers.CharField(source='product.product_name', read_only=True) # Expose product name
    product_id_for_reviews = serializers.SerializerMethodField(read_only=True) # Expose product_id for reviews
    product_unit_display = serializers.SerializerMethodField(read_only=True) # Expose product unit
    product_description = serializers.SerializerMethodField(read_only=True) # Expose product description
    product_is_perishable = serializers.SerializerMethodField(read_only=True) # Expose product is_perishable
    product_shelf_life_days = serializers.SerializerMethodField(read_only=True) # Expose product shelf_life_days
    status_display = serializers.CharField(source='get_listing_status_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_grade_display', read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)
    sample_review_comment = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ProductListing
        fields = [
            'listing_id', 'farmer', 'farmer_name', 'farm', 'farm_name', 'product',
            'current_price', 'quantity_available', 'min_order_quantity',
            'harvest_date', 'expected_harvest_date', 'quality_grade', 'quality_display',
            'is_organic_certified', 'listing_status', 'status_display', 'photos', 'notes',
            'created_at', 'updated_at', 'average_rating', 'review_count', 'sample_review_comment',
            'product_name', 'product_id_for_reviews', 'product_unit_display', 'product_description',
            'product_is_perishable', 'product_shelf_life_days'
        ]
        read_only_fields = [
            'listing_id', 'farmer', 'created_at', 'updated_at', 'farmer_name', 'farm_name',
            'product_name', 'product_id_for_reviews', 'product_unit_display', 'product_description',
            'product_is_perishable', 'product_shelf_life_days'
        ]
    
    def get_farmer_name(self, obj):
        return obj.farmer.get_full_name()
    
    def get_farm_name(self, obj):
        return obj.farm.farm_name

    def get_product_id_for_reviews(self, obj):
        return obj.product.product_id

    def get_product_unit_display(self, obj):
        return obj.product.get_unit_of_measure_display()

    def get_product_description(self, obj):
        return obj.product.description

    def get_product_is_perishable(self, obj):
        return obj.product.is_perishable

    def get_product_shelf_life_days(self, obj):
        return obj.product.shelf_life_days

    def get_average_rating(self, obj):
        """Calculate the average rating for the product associated with this listing"""
        # Filter reviews for this product listing and ensure they are visible
        reviews = Review.objects.filter(
            target_type='product', 
            target_id=obj.product.product_id,
            is_visible=True
        )
        return reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0

    def get_review_count(self, obj):
        """Count the number of visible reviews for the product associated with this listing"""
        # Filter reviews for this product listing and ensure they are visible
        return Review.objects.filter(
            target_type='product', 
            target_id=obj.product.product_id,
            is_visible=True
        ).count()

    def get_sample_review_comment(self, obj):
        """Return a sample review comment for the product associated with this listing"""
        review = Review.objects.filter(
            target_type='product',
            target_id=obj.product.product_id,
            is_visible=True,
            comment__isnull=False
        ).exclude(comment__exact='').order_by('-review_date').first()
        return review.comment if review else None
    
    def validate_farm(self, value):
        """Ensure the farm belongs to the farmer"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not Farm.objects.filter(farm_id=value.farm_id, farmer=user).exists():
                raise serializers.ValidationError("You can only create listings for farms you own.")
        return value
    
    # Removed validate_product method as PrimaryKeyRelatedField handles existence
    
    def validate(self, data):
        """Validate the data"""
        # Get the instance being updated, if any
        instance = self.instance
        
        # Determine the effective listing_status for validation
        # If listing_status is provided in data, use it. Otherwise, use the instance's current status.
        effective_listing_status = data.get('listing_status', instance.listing_status if instance else None)

        # Ensure quantity_available is positive only if status is 'available' or 'pre_order'
        # If quantity_available is not provided in data, use the instance's current value.
        current_quantity_available = data.get('quantity_available', instance.quantity_available if instance else 0)

        if effective_listing_status in ['available', 'pre_order'] and current_quantity_available <= 0:
            raise serializers.ValidationError({"quantity_available": "Quantity available must be positive for active listings."})
        
        # Ensure min_order_quantity is positive and not greater than quantity_available
        min_order = data.get('min_order_quantity', instance.min_order_quantity if instance else 1)
        if min_order <= 0:
            raise serializers.ValidationError({"min_order_quantity": "Minimum order quantity must be positive."})
        
        # Only validate min_order_quantity against quantity_available if quantity_available is provided or exists
        if 'quantity_available' in data or instance:
            if min_order > current_quantity_available:
                raise serializers.ValidationError({"min_order_quantity": "Minimum order quantity cannot exceed quantity available."})
        
        # Ensure current_price is positive
        if data.get('current_price', instance.current_price if instance else 0) <= 0:
            raise serializers.ValidationError({"current_price": "Price must be positive."})
        
        # Validate dates
        harvest_date = data.get('harvest_date', instance.harvest_date if instance else None)
        expected_harvest_date = data.get('expected_harvest_date', instance.expected_harvest_date if instance else None)
        
        if harvest_date and expected_harvest_date and harvest_date != expected_harvest_date:
            raise serializers.ValidationError({"harvest_date": "Cannot specify both actual and expected harvest dates with different values."})
        
        # If listing status is pre_order, expected_harvest_date is required
        if effective_listing_status == 'pre_order' and not expected_harvest_date:
            raise serializers.ValidationError({"expected_harvest_date": "Expected harvest date is required for pre-order listings."})
        
        # If listing status is available and no harvest_date, set it to today
        if effective_listing_status == 'available' and not harvest_date and not expected_harvest_date:
            data['harvest_date'] = timezone.now().date()
        
        return data
    
    def create(self, validated_data):
        # Set the farmer to the current user
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle photos field separately as it's a JSONField storing a list of URLs
        photos_data = validated_data.pop('photos', None)
        if photos_data is not None:
            instance.photos = photos_data # Update the photos list directly

        # Call the super method to handle other fields
        return super().update(instance, validated_data)