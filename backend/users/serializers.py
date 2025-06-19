from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

User = get_user_model()

class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Custom user creation serializer for Djoser.
    
    NOTE: This serializer is configured but not used due to a framework-level issue
    where Djoser doesn't properly call custom serializers for user creation.
    
    The application uses /api/users/register/ custom endpoint instead for reliable
    user registration with email field support.
    
    This serializer is kept for:
    - Documentation purposes
    - Potential future Djoser fixes
    - Consistency with Djoser configuration
    """
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['phone_number', 'email', 'first_name', 'last_name', 'password', 'user_role']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False, 'allow_blank': True},
        }

class UserSerializer(BaseUserSerializer):
    unread_notifications_count = serializers.ReadOnlyField()
    unread_messages_count = serializers.ReadOnlyField()
    
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['user_id', 'phone_number', 'email', 'first_name', 'last_name', 
                 'user_role', 'profile_photo_url', 'preferred_language', 
                 'is_active', 'is_verified', 'sms_notifications', 'email_notifications',
                 'marketing_notifications', 'order_updates', 'weather_alerts', 'price_alerts',
                 'unread_notifications_count', 'unread_messages_count', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'is_verified', 
                           'unread_notifications_count', 'unread_messages_count']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_photo_url', 
                 'preferred_language', 'sms_notifications', 'email_notifications',
                 'marketing_notifications', 'order_updates', 'weather_alerts', 'price_alerts']
        extra_kwargs = {
            'email': {'required': False},
        }
    
    def validate_email(self, value):
        if value and User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value

class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Dedicated serializer for updating notification preferences"""
    class Meta:
        model = User
        fields = ['sms_notifications', 'email_notifications', 'marketing_notifications', 
                 'order_updates', 'weather_alerts', 'price_alerts']
    
    def validate_weather_alerts(self, value):
        """Only farmers should be able to enable weather alerts"""
        if value and self.instance.user_role != 'farmer':
            raise serializers.ValidationError("Weather alerts are only available for farmers.")
        return value