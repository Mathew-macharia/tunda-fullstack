from rest_framework import serializers
from .models import SystemSettings

class SystemSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the SystemSettings model
    """
    value = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemSettings
        fields = ['setting_id', 'setting_key', 'setting_value', 'setting_type', 'description', 'value']
        read_only_fields = ['setting_id']
    
    def get_value(self, obj):
        """
        Return the typed value of the setting
        """
        return obj.get_typed_value()

class SystemSettingsCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating or updating system settings
    """
    class Meta:
        model = SystemSettings
        fields = ['setting_key', 'setting_value', 'setting_type', 'description']
        
    def validate(self, data):
        """
        Validate that the setting value is compatible with the setting type
        """
        setting_value = data.get('setting_value')
        setting_type = data.get('setting_type')
        
        if setting_type == 'number':
            try:
                float(setting_value)
            except ValueError:
                raise serializers.ValidationError({"setting_value": "Value must be a valid number."})
        elif setting_type == 'boolean':
            if setting_value.lower() not in ['true', 'false']:
                raise serializers.ValidationError({"setting_value": "Value must be 'true' or 'false'."})
        elif setting_type == 'json':
            try:
                import json
                json.loads(setting_value)
            except:
                raise serializers.ValidationError({"setting_value": "Value must be valid JSON."})
                
        return data
