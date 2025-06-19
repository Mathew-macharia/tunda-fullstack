from rest_framework import serializers
from .models import Farm
from locations.models import SubCounty
from django.contrib.auth import get_user_model

User = get_user_model()

class FarmSerializer(serializers.ModelSerializer):
    farmer_name = serializers.SerializerMethodField(read_only=True)
    location_name = serializers.SerializerMethodField(read_only=True)
    
    # Map frontend location_id to sub_county_id
    location_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Farm
        fields = [
            'farm_id', 'farmer', 'farmer_name', 'farm_name', 
            'location_id', 'location_name', 'total_acreage', 'cultivated_area', 
            'farm_description', 'farm_photos', 'is_certified_organic', 
            'soil_type', 'water_source', 'weather_zone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['farm_id', 'farmer', 'created_at', 'updated_at']
    
    def get_farmer_name(self, obj):
        return obj.farmer.get_full_name()
    
    def get_location_name(self, obj):
        return obj.location_name
    
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
