from rest_framework import serializers
from .models import MarketPrice, WeatherAlert
from products.models import Product
from locations.models import Location

class MarketPriceSerializer(serializers.ModelSerializer):
    """Serializer for the MarketPrice model"""
    product_name = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketPrice
        fields = [
            'price_id', 'product', 'product_name', 'location', 'location_name',
            'average_price', 'min_price', 'max_price', 'price_date',
            'data_source', 'created_at'
        ]
        read_only_fields = ['price_id', 'created_at']
    
    def get_product_name(self, obj):
        """Return the name of the product"""
        return obj.product.product_name
    
    def get_location_name(self, obj):
        """Return the name of the location"""
        return obj.location.location_name
    
    def validate(self, data):
        """Validate that min_price <= average_price <= max_price"""
        min_price = data.get('min_price')
        avg_price = data.get('average_price')
        max_price = data.get('max_price')
        
        if min_price > avg_price:
            raise serializers.ValidationError({
                'min_price': 'Minimum price cannot be greater than the average price'
            })
        
        if avg_price > max_price:
            raise serializers.ValidationError({
                'average_price': 'Average price cannot be greater than the maximum price'
            })
        
        # Check for uniqueness constraint
        product = data.get('product')
        location = data.get('location')
        price_date = data.get('price_date')
        
        # Only check for existing records when creating a new one
        if self.instance is None:  # This is a create operation
            if MarketPrice.objects.filter(
                product=product,
                location=location,
                price_date=price_date
            ).exists():
                raise serializers.ValidationError({
                    'non_field_errors': 'A price record already exists for this product, location, and date'
                })
        
        return data


class WeatherAlertSerializer(serializers.ModelSerializer):
    """Serializer for the WeatherAlert model"""
    location_name = serializers.SerializerMethodField()
    alert_type_display = serializers.SerializerMethodField()
    severity_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WeatherAlert
        fields = [
            'alert_id', 'location', 'location_name', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'alert_message', 'start_date', 
            'end_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['alert_id', 'created_at']
    
    def get_location_name(self, obj):
        """Return the name of the location"""
        return obj.location.location_name
    
    def get_alert_type_display(self, obj):
        """Return the display name of the alert type"""
        return obj.get_alert_type_display()
    
    def get_severity_display(self, obj):
        """Return the display name of the severity"""
        return obj.get_severity_display()
    
    def validate(self, data):
        """Validate that start_date <= end_date if end_date is provided"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'End date cannot be before the start date'
            })
        
        return data
