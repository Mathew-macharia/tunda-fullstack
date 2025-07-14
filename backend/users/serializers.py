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

class AdminUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin user creation that properly handles password validation and hashing.
    """
    password = serializers.CharField(write_only=True, min_length=6)
    re_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['phone_number', 'email', 'first_name', 'last_name', 
                 'user_role', 'password', 're_password', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
            're_password': {'write_only': True},
            'email': {'required': False, 'allow_blank': True},
        }
    
    def validate_password(self, value):
        """Validate password using Django's built-in validators"""
        validate_password(value)
        return value
    
    def validate_user_role(self, value):
        """Validate user role"""
        valid_roles = ['customer', 'farmer', 'rider', 'admin']
        if value not in valid_roles:
            raise serializers.ValidationError(f'Invalid user role. Must be one of: {", ".join(valid_roles)}')
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness"""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness if provided"""
        if value and value.strip():
            value = value.strip()
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
            return value
        return None
    
    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create user with proper password hashing"""
        # Remove re_password before creating user
        validated_data.pop('re_password', None)
        password = validated_data.pop('password')
        
        # Clean email field
        email = validated_data.get('email')
        if email and not email.strip():
            validated_data['email'] = None
        
        # Create user with proper password hashing using the custom user manager
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

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