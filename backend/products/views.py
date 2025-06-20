from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from .models import ProductCategory, Product, ProductListing
from .serializers import ProductCategorySerializer, ProductSerializer, ProductListingSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects,
    but allow anyone to view them.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.user_role == 'admin')

class IsFarmerAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow farmers and admins to edit products,
    but allow anyone to view them.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to farmers and admin users
        return request.user and request.user.is_authenticated and (
            request.user.user_role == 'farmer' or 
            request.user.user_role == 'admin' or 
            request.user.is_staff
        )

class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product categories.
    Anyone can view categories, but only admins can create/edit/delete.
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category_name', 'description']
    ordering_fields = ['category_name']
    ordering = ['category_name']  # Default ordering
    
    def get_queryset(self):
        queryset = ProductCategory.objects.all()
        
        # Filter by parent_category_id if provided
        parent_id = self.request.query_params.get('parent_id', None)
        if parent_id is not None:
            if parent_id == '0' or parent_id.lower() == 'null':
                # Return root categories
                queryset = queryset.filter(parent_category__isnull=True)
            else:
                # Return children of specified parent
                queryset = queryset.filter(parent_category_id=parent_id)
                
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """
        Return the child categories of this category
        """
        category = self.get_object()
        children = ProductCategory.objects.filter(parent_category=category)
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Return the products in this category
        """
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products.
    Anyone can view products, but only farmers and admins can create/edit/delete.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsFarmerAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name', 'description']
    ordering_fields = ['product_name', 'created_at', 'category__category_name']
    ordering = ['product_name']  # Default ordering
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filter by category_id if provided
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
            
        # Filter by is_active if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
            
        # Filter by is_perishable if provided
        is_perishable = self.request.query_params.get('is_perishable', None)
        if is_perishable is not None:
            is_perishable_bool = is_perishable.lower() == 'true'
            queryset = queryset.filter(is_perishable=is_perishable_bool)
            
        # Filter by shelf_life_days if provided
        shelf_life = self.request.query_params.get('shelf_life', None)
        if shelf_life is not None:
            try:
                shelf_life_days = int(shelf_life)
                queryset = queryset.filter(shelf_life_days__lte=shelf_life_days)
            except ValueError:
                pass  # Ignore invalid shelf_life parameter
                
        return queryset
    
    @action(detail=False, methods=['get'])
    def perishable(self, request):
        """
        Return only perishable products
        """
        queryset = Product.objects.filter(is_perishable=True, is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def non_perishable(self, request):
        """
        Return only non-perishable products
        """
        queryset = Product.objects.filter(is_perishable=False, is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class IsFarmerOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow farmers to manage only their own listings.
    Anyone can view available/pre_order listings.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request for list/retrieve
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to authenticated farmers
        return request.user and request.user.is_authenticated and request.user.user_role == 'farmer'
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner of the listing
        return obj.farmer == request.user

class ProductListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product listings.
    Anyone can view active listings, but only farmers can create/edit/delete their own listings.
    """
    serializer_class = ProductListingSerializer
    permission_classes = [IsFarmerOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__product_name', 'farm__farm_name', 'notes']
    ordering_fields = ['current_price', 'created_at', 'harvest_date', 'expected_harvest_date']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        user = self.request.user
        
        # Basic queryset - for admin or staff, show all
        if user.is_authenticated and (user.is_staff or user.user_role == 'admin'):
            queryset = ProductListing.objects.all()
        # For farmers, show their own listings (all statuses)
        elif user.is_authenticated and user.user_role == 'farmer':
            queryset = ProductListing.objects.filter(farmer=user)
        # For other users or unauthenticated users, show only available or pre_order listings
        else:
            queryset = ProductListing.objects.filter(
                Q(listing_status='available') | Q(listing_status='pre_order')
            )
        
        # Apply filters from query parameters
        
        # Filter by farmer_id
        farmer_id = self.request.query_params.get('farmer_id')
        if farmer_id:
            queryset = queryset.filter(farmer_id=farmer_id)
        
        # Filter by farm_id
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        # Filter by product_id
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by listing_status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(listing_status=status)
        
        # Filter by quality_grade
        quality = self.request.query_params.get('quality')
        if quality:
            queryset = queryset.filter(quality_grade=quality)
        
        # Filter by is_organic_certified
        organic = self.request.query_params.get('organic')
        if organic is not None:
            is_organic = organic.lower() == 'true'
            queryset = queryset.filter(is_organic_certified=is_organic)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                # Use Decimal to avoid floating point issues
                queryset = queryset.filter(current_price__gte=Decimal(min_price))
            except (ValueError, InvalidOperation):
                pass
        
        if max_price:
            try:
                # Use Decimal to avoid floating point issues
                queryset = queryset.filter(current_price__lte=Decimal(max_price))
            except (ValueError, InvalidOperation):
                pass
        
        # Filter by available date
        available_date = self.request.query_params.get('available_date')
        if available_date:
            try:
                date_obj = timezone.datetime.strptime(available_date, '%Y-%m-%d').date()
                queryset = queryset.filter(
                    Q(harvest_date__lte=date_obj) | Q(expected_harvest_date__lte=date_obj)
                )
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_sold_out(self, request, pk=None):
        """
        Mark a listing as sold out
        """
        listing = self.get_object()
        listing.listing_status = 'sold_out'
        listing.save()
        serializer = self.get_serializer(listing)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_available(self, request, pk=None):
        """
        Mark a listing as available
        """
        listing = self.get_object()
        
        # Ensure there's either a harvest_date or expected_harvest_date
        if not listing.harvest_date and not listing.expected_harvest_date:
            listing.harvest_date = timezone.now().date()
        
        listing.listing_status = 'available'
        listing.save()
        serializer = self.get_serializer(listing)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_inactive(self, request, pk=None):
        """
        Mark a listing as inactive
        """
        listing = self.get_object()
        listing.listing_status = 'inactive'
        listing.save()
        serializer = self.get_serializer(listing)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_pre_order(self, request, pk=None):
        """
        Mark a listing as pre-order
        """
        listing = self.get_object()
        
        # Ensure there's an expected_harvest_date
        if not listing.expected_harvest_date:
            return Response(
                {"error": "Expected harvest date is required for pre-order listings."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        listing.listing_status = 'pre_order'
        listing.save()
        serializer = self.get_serializer(listing)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """
        Return the authenticated farmer's listings
        """
        if not request.user.is_authenticated or request.user.user_role != 'farmer':
            return Response(
                {"error": "Only authenticated farmers can view their listings."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = ProductListing.objects.filter(farmer=request.user)
        
        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(listing_status=status_param)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_farm(self, request):
        """
        Return listings for a specific farm
        """
        farm_id = request.query_params.get('farm_id')
        if not farm_id:
            return Response(
                {"error": "Farm ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        
        # For farmers, ensure they can only see their own farm's listings
        if user.is_authenticated and user.user_role == 'farmer':
            queryset = ProductListing.objects.filter(farm_id=farm_id, farmer=user)
        # For admin/staff, show all farm listings
        elif user.is_authenticated and (user.is_staff or user.user_role == 'admin'):
            queryset = ProductListing.objects.filter(farm_id=farm_id)
        # For other users, show only available/pre_order listings
        else:
            queryset = ProductListing.objects.filter(
                farm_id=farm_id, 
                listing_status__in=['available', 'pre_order']
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
