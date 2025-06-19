from rest_framework import serializers
from .models import Location, County, SubCounty, UserAddress

class LocationSerializer(serializers.ModelSerializer):
    """DEPRECATED: Use UserAddressSerializer instead"""
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ('user',)

class CountySerializer(serializers.ModelSerializer):
    """Serializer for County reference data"""
    class Meta:
        model = County
        fields = ['county_id', 'county_name', 'county_code']

class SubCountySerializer(serializers.ModelSerializer):
    """Serializer for SubCounty reference data"""
    county_name = serializers.CharField(source='county.county_name', read_only=True)
    
    class Meta:
        model = SubCounty
        fields = ['sub_county_id', 'county', 'sub_county_name', 'sub_county_code', 'county_name']

class UserAddressSerializer(serializers.ModelSerializer):
    """Serializer for user delivery addresses"""
    county_name = serializers.CharField(source='county.county_name', read_only=True)
    sub_county_name = serializers.CharField(source='sub_county.sub_county_name', read_only=True)
    
    class Meta:
        model = UserAddress
        fields = [
            'address_id', 'full_name', 'phone_number', 'county', 'county_name',
            'sub_county', 'sub_county_name', 'location_name', 'detailed_address',
            'latitude', 'longitude', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def validate(self, data):
        """Ensure sub_county belongs to the selected county"""
        if 'county' in data and 'sub_county' in data:
            if data['sub_county'].county != data['county']:
                raise serializers.ValidationError(
                    "Sub-county must belong to the selected county"
                )
        return data

