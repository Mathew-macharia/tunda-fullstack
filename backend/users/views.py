from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.http import HttpResponse
from .serializers import UserProfileUpdateSerializer, ChangePasswordSerializer, UserSerializer, AdminUserCreateSerializer
import csv
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_role == 'admin'

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({"message": "Password updated successfully."}, 
                            status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing all users in the system.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'last_login', 'first_name', 'user_role']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Return different serializers for different actions.
        Use AdminUserCreateSerializer for creation, UserSerializer for everything else.
        """
        if self.action == 'create':
            return AdminUserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create method to use AdminUserCreateSerializer and return UserSerializer data.
        """
        # Use AdminUserCreateSerializer for creation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return the created user data using UserSerializer for consistent response format
        response_serializer = UserSerializer(user)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter by role
        user_role = self.request.query_params.get('user_role', None)
        if user_role:
            queryset = queryset.filter(user_role=user_role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter by date range
        date_range = self.request.query_params.get('date_range', None)
        if date_range:
            now = timezone.now()
            if date_range == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_range == 'week':
                start_date = now - timedelta(days=7)
            elif date_range == 'month':
                start_date = now - timedelta(days=30)
            elif date_range == 'year':
                start_date = now - timedelta(days=365)
            else:
                start_date = None
            
            if start_date:
                queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get user statistics for admin dashboard
        """
        total_users = User.objects.count()
        stats = User.objects.values('user_role').annotate(count=Count('user_role'))
        
        role_counts = {
            'total': total_users,
            'farmers': 0,
            'customers': 0,
            'riders': 0,
            'admins': 0
        }
        
        for stat in stats:
            if stat['user_role'] == 'farmer':
                role_counts['farmers'] = stat['count']
            elif stat['user_role'] == 'customer':
                role_counts['customers'] = stat['count']
            elif stat['user_role'] == 'rider':
                role_counts['riders'] = stat['count']
            elif stat['user_role'] == 'admin':
                role_counts['admins'] = stat['count']
        
        return Response(role_counts)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export users to CSV
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Phone Number', 'Email', 'First Name', 'Last Name', 
            'Role', 'Active', 'Date Joined', 'Last Login'
        ])
        
        for user in queryset:
            writer.writerow([
                user.user_id,
                user.phone_number,
                user.email or '',
                user.first_name,
                user.last_name,
                user.user_role,
                'Yes' if user.is_active else 'No',
                user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
            ])
        
        return response

    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        """
        Toggle user active status
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Reset user password (admin only)
        """
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response(
                {'error': 'new_password is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password reset successfully'})

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user_with_email(request):
    """
    Custom user creation endpoint that properly handles email field.
    
    This endpoint is used instead of Djoser's default /users/users/ endpoint
    because of issues with email field handling in the Djoser serializer.
    
    Expected payload:
    {
        "phone_number": "0712345678",
        "password": "secure_password",
        "re_password": "secure_password",
        "first_name": "John",
        "last_name": "Doe", 
        "user_role": "customer|farmer|rider|admin",
        "email": "user@example.com" (optional)
    }
    """
    data = request.data
    required_fields = ['phone_number', 'password', 're_password', 'first_name', 'last_name', 'user_role']
    
    # Validate required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return Response({field: 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password match
    if data['password'] != data['re_password']:
        return Response({'password': "Password fields didn't match."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate user role
    valid_roles = ['customer', 'farmer', 'rider', 'admin']
    if data['user_role'] not in valid_roles:
        return Response({'user_role': f'Invalid user role. Must be one of: {", ".join(valid_roles)}'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already exists
    if User.objects.filter(phone_number=data['phone_number']).exists():
        return Response({'phone_number': 'A user with this phone number already exists.'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check if email already exists (if provided)
    email = data.get('email', None)
    if email and email.strip():
        email = email.strip()
        if User.objects.filter(email=email).exists():
            return Response({'email': 'A user with this email already exists.'}, 
                           status=status.HTTP_400_BAD_REQUEST)
    else:
        email = None
    
    try:
        # Create user
        user = User.objects.create_user(
            phone_number=data['phone_number'],
            password=data['password'],
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            user_role=data['user_role'],
            email=email
        )
        
        # Return user data using the UserSerializer
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': f'Failed to create user: {str(e)}'}, 
                       status=status.HTTP_400_BAD_REQUEST)