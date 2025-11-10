from rest_framework import serializers
from rest_framework import serializers
from django.db.models import Avg, Count # Import Count for review_count
from .models import Farm
from locations.models import SubCounty
from django.contrib.auth import get_user_model
from products.models import ProductListing, Product
from feedback.models import Review
from orders.models import OrderItem

User = get_user_model()

class FarmSerializer(serializers.ModelSerializer):
    farmer_id = serializers.SerializerMethodField(read_only=True)
    farmer_name = serializers.SerializerMethodField(read_only=True)
    location_name = serializers.SerializerMethodField(read_only=True)
    profile_photo_url = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)
    active_listings_count = serializers.SerializerMethodField(read_only=True)
    product_count = serializers.SerializerMethodField(read_only=True)
    total_orders_completed = serializers.SerializerMethodField(read_only=True)
    number_of_farms = serializers.SerializerMethodField(read_only=True)

    location_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Farm
        fields = [
            'farm_id', 'farmer', 'farmer_id', 'farmer_name', 'farm_name',
            'location_id', 'location_name', 'total_acreage', 'cultivated_area',
            'farm_description', 'farm_photos', 'is_certified_organic',
            'soil_type', 'water_source', 'weather_zone', 'created_at', 'updated_at',
            'profile_photo_url', 'average_rating', 'review_count', 'active_listings_count',
            'product_count', 'total_orders_completed', 'number_of_farms'
        ]
        read_only_fields = ['farm_id', 'farmer', 'created_at', 'updated_at']

    def get_farmer_id(self, obj):
        return obj.farmer.user_id

    def get_farmer_name(self, obj):
        return obj.farmer.get_full_name()

    def get_location_name(self, obj):
        return obj.location_name

    def get_profile_photo_url(self, obj):
        return obj.farmer.profile_photo_url if obj.farmer.profile_photo_url else None

    def get_average_rating(self, obj):
        return obj.farmer_rating

    def get_review_count(self, obj):
        return Review.objects.filter(
            target_type='farmer',
            target_id=str(obj.farmer.user_id),
            is_visible=True
        ).count()

    def get_active_listings_count(self, obj):
        return ProductListing.objects.filter(
            farmer=obj.farmer,
            listing_status__in=['available', 'pre_order']
        ).count()

    def get_product_count(self, obj):
        return ProductListing.objects.filter(farmer=obj.farmer).values('product').distinct().count()

    def get_total_orders_completed(self, obj):
        return OrderItem.objects.filter(
            farmer=obj.farmer,
            order__order_status='delivered'
        ).values('order').distinct().count()

    def get_number_of_farms(self, obj):
        return obj.farmer.farms.count()
    
    def validate_location_id(self, value):
        """Validate that the sub_county_id exists"""
        try:
            SubCounty.objects.get(sub_county_id=value)
            return value
        except SubCounty.DoesNotExist:
            raise serializers.ValidationError("Selected sub-county does not exist.")
    
    def validate_weather_zone(self, value):
        """Validate weather zone - if not in choices, default to highland"""
        valid_choices = ['highland', 'midland', 'lowland']
        if value not in valid_choices:
            return 'highland'
        return value
    
    def validate(self, attrs):
        """Handle location_id to sub_county mapping"""
        if 'location_id' in attrs:
            location_id = attrs.pop('location_id')
            try:
                subcounty = SubCounty.objects.get(sub_county_id=location_id)
                attrs['sub_county'] = subcounty
            except SubCounty.DoesNotExist:
                raise serializers.ValidationError("Selected sub-county does not exist.")
        
        return super().validate(attrs)
    
    def create(self, validated_data):
        # Set the current user as the farmer
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Add sub_county info to the response"""
        data = super().to_representation(instance)
        if instance.sub_county:
            data['sub_county'] = {
                'sub_county_id': instance.sub_county.sub_county_id,
                'sub_county_name': instance.sub_county.sub_county_name,
                'county': {
                    'county_id': instance.sub_county.county.county_id,
                    'county_name': instance.sub_county.county.county_name
                }
            }
        return data
