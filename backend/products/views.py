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
        
        # Filter by product_id (for specific product filtering)
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        # Filter by product category
        category_id = self.request.query_params.get('category') # Changed parameter name to 'category'
        if category_id:
            queryset = queryset.filter(product__category_id=category_id)
        
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

    @action(detail=False, methods=['post'])
    def upload_photo(self, request):
        """
        Upload a photo for a product listing
        """
        try:
            photo = request.FILES['photo']
            # Generate a unique filename
            import uuid
            filename = f"{uuid.uuid4()}.{photo.name.split('.')[-1]}"
            
            # Save the file to MEDIA_ROOT/product_photos
            import os
            from django.conf import settings
            
            # Ensure the directory exists
            photo_dir = os.path.join(settings.MEDIA_ROOT, 'product_photos')
            os.makedirs(photo_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(photo_dir, filename)
            with open(file_path, 'wb+') as destination:
                for chunk in photo.chunks():
                    destination.write(chunk)
            
            # Return the URL
            photo_url = f"{settings.MEDIA_URL}product_photos/{filename}"
            return Response({'url': photo_url}, status=status.HTTP_201_CREATED)
            
        except KeyError:
            return Response({'error': 'No photo provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def active_farmers(self, request):
        """
        Return farmers who have active product listings with their details.
        Public endpoint - no authentication required.
        """
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Avg, Q
        
        User = get_user_model()
        
        # Get unique farmers with active listings
        active_farmers = User.objects.filter(
            user_role='farmer',
            product_listings__listing_status__in=['available', 'pre_order']
        ).distinct().annotate(
            active_listings_count=Count(
                'product_listings',
                filter=Q(product_listings__listing_status__in=['available', 'pre_order'])
            )
        )
        
        farmers_data = []
        for farmer in active_farmers:
            # Calculate farmer rating from reviews
            try:
                from feedback.models import Review
                reviews = Review.objects.filter(
                    target_type='farmer',
                    target_id=farmer.user_id,
                    is_visible=True
                )
                avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
                review_count = reviews.count()
            except:
                avg_rating = 0
                review_count = 0
            
            farmers_data.append({
                'farmer_id': farmer.user_id,
                'farmer_name': farmer.get_full_name(),
                'profile_photo_url': farmer.profile_photo_url,
                'active_listings_count': farmer.active_listings_count,
                'average_rating': round(float(avg_rating), 1) if avg_rating else 0.0,
                'review_count': review_count
            })
        
        # Sort by rating (highest first), then by name
        farmers_data.sort(key=lambda x: (-x['average_rating'], x['farmer_name']))
        
        return Response(farmers_data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def farmer_detail(self, request):
        """
        Get complete farmer profile with farms, sample products, and statistics.
        Public endpoint - returns only public-safe data.
        
        Query params:
            farmer_id: ID of the farmer
        """
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Avg, Q
        from farms.models import Farm
        
        User = get_user_model()
        farmer_id = request.query_params.get('farmer_id')
        
        if not farmer_id:
            return Response(
                {'error': 'farmer_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            farmer = User.objects.get(user_id=farmer_id, user_role='farmer')
        except User.DoesNotExist:
            return Response(
                {'error': 'Farmer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get farmer's rating from reviews
        try:
            from feedback.models import Review
            reviews = Review.objects.filter(
                target_type='farmer',
                target_id=farmer.user_id,
                is_visible=True
            )
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            review_count = reviews.count()
        except:
            avg_rating = 0
            review_count = 0
        
        # Get farmer's farms with product counts
        farms = Farm.objects.filter(farmer=farmer).annotate(
            products_count=Count(
                'product_listings',
                filter=Q(product_listings__listing_status__in=['available', 'pre_order'])
            )
        )
        
        farms_data = []
        for farm in farms:
            farms_data.append({
                'farm_id': farm.farm_id,
                'farm_name': farm.farm_name,
                'location': f"{farm.sub_county.sub_county_name}, {farm.sub_county.county.county_name}",
                'sub_county': farm.sub_county.sub_county_name,
                'county': farm.sub_county.county.county_name,
                'is_certified_organic': farm.is_certified_organic,
                'farm_photos': farm.farm_photos if farm.farm_photos else [],
                'products_count': farm.products_count,
                'created_at': farm.created_at.isoformat()
            })
        
        # Get sample products (up to 10 active listings)
        sample_listings = ProductListing.objects.filter(
            farmer=farmer,
            listing_status__in=['available', 'pre_order']
        ).select_related('product', 'farm').order_by('-created_at')[:10]
        
        sample_products = []
        for listing in sample_listings:
            sample_products.append({
                'listing_id': listing.listing_id,
                'product_name': listing.product.product_name,
                'current_price': str(listing.current_price),
                'product_unit_display': listing.product.get_unit_of_measure_display(),
                'photos': listing.photos if listing.photos else [],
                'farm_name': listing.farm.farm_name,
                'listing_status': listing.listing_status,
                'is_organic_certified': listing.is_organic_certified,
                'quantity_available': str(listing.quantity_available)
            })
        
        # Get total statistics
        total_products = ProductListing.objects.filter(
            farmer=farmer,
            listing_status__in=['available', 'pre_order']
        ).count()
        
        # Get total orders/sales count (if orders app available)
        try:
            from orders.models import OrderItem
            total_sales = OrderItem.objects.filter(farmer=farmer).count()
        except:
            total_sales = 0
        
        # Count organic products
        organic_products = ProductListing.objects.filter(
            farmer=farmer,
            listing_status__in=['available', 'pre_order'],
            is_organic_certified=True
        ).count()
        
        # Get primary location (most common county from farms)
        primary_location = None
        if farms.exists():
            primary_location = farms.first().sub_county.county.county_name
        
        farmer_data = {
            'farmer_id': farmer.user_id,
            'farmer_name': farmer.get_full_name(),
            'profile_photo_url': farmer.profile_photo_url,
            'average_rating': round(float(avg_rating), 1) if avg_rating else 0.0,
            'review_count': review_count,
            'total_products': total_products,
            'farms_count': farms.count(),
            'member_since': farmer.created_at.isoformat(),
            'primary_location': primary_location,
            'farms': farms_data,
            'sample_products': sample_products,
            'statistics': {
                'total_sales': total_sales,
                'organic_products': organic_products,
                'total_farms': farms.count()
            }
        }
        
        return Response(farmer_data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def farm_detail(self, request):
        """
        Get complete farm details with sample products.
        Public endpoint - returns only public-safe data.
        
        Query params:
            farm_id: ID of the farm
        """
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Avg, Q
        from farms.models import Farm
        
        User = get_user_model()
        farm_id = request.query_params.get('farm_id')
        
        if not farm_id:
            return Response(
                {'error': 'farm_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            farm = Farm.objects.select_related('farmer', 'sub_county__county').get(farm_id=farm_id)
        except Farm.DoesNotExist:
            return Response(
                {'error': 'Farm not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get farmer's rating
        try:
            from feedback.models import Review
            reviews = Review.objects.filter(
                target_type='farmer',
                target_id=farm.farmer.user_id,
                is_visible=True
            )
            farmer_avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            farmer_review_count = reviews.count()
        except:
            farmer_avg_rating = 0
            farmer_review_count = 0
        
        # Get sample products from this farm (6-8 active listings)
        sample_listings = ProductListing.objects.filter(
            farm=farm,
            listing_status__in=['available', 'pre_order']
        ).select_related('product').order_by('-created_at')[:8]
        
        sample_products = []
        for listing in sample_listings:
            # Get product rating
            try:
                from feedback.models import Review
                product_reviews = Review.objects.filter(
                    target_type='product',
                    target_id=listing.product.product_id,
                    is_visible=True
                )
                product_avg_rating = product_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
                product_review_count = product_reviews.count()
            except:
                product_avg_rating = 0
                product_review_count = 0
            
            sample_products.append({
                'listing_id': listing.listing_id,
                'product_name': listing.product.product_name,
                'current_price': str(listing.current_price),
                'product_unit_display': listing.product.get_unit_of_measure_display(),
                'photos': listing.photos if listing.photos else [],
                'listing_status': listing.listing_status,
                'is_organic_certified': listing.is_organic_certified,
                'quantity_available': str(listing.quantity_available),
                'min_order_quantity': str(listing.min_order_quantity),
                'average_rating': round(float(product_avg_rating), 1) if product_avg_rating else 0.0,
                'review_count': product_review_count
            })
        
        # Get total products count from this farm
        total_products = ProductListing.objects.filter(
            farm=farm,
            listing_status__in=['available', 'pre_order']
        ).count()
        
        # Get unique product categories from this farm
        product_categories = ProductListing.objects.filter(
            farm=farm,
            listing_status__in=['available', 'pre_order']
        ).values_list('product__category__category_name', flat=True).distinct()
        
        farm_data = {
            'farm_id': farm.farm_id,
            'farm_name': farm.farm_name,
            'farmer_id': farm.farmer.user_id,
            'farmer_name': farm.farmer.get_full_name(),
            'farmer_profile_photo': farm.farmer.profile_photo_url,
            'farmer_average_rating': round(float(farmer_avg_rating), 1) if farmer_avg_rating else 0.0,
            'farmer_review_count': farmer_review_count,
            'location': {
                'sub_county': farm.sub_county.sub_county_name,
                'county': farm.sub_county.county.county_name,
                'full_location': f"{farm.sub_county.sub_county_name}, {farm.sub_county.county.county_name}"
            },
            'farm_description': farm.farm_description,
            'farm_photos': farm.farm_photos if farm.farm_photos else [],
            'is_certified_organic': farm.is_certified_organic,
            'weather_zone': farm.weather_zone,
            'weather_zone_display': farm.get_weather_zone_display(),
            'created_at': farm.created_at.isoformat(),
            'total_products': total_products,
            'product_categories': list(product_categories),
            'sample_products': sample_products
        }
        
        return Response(farm_data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def related_farmers(self, request):
        """
        Get related farmers based on location and product similarity.
        Uses intelligent scoring algorithm to find the most relevant farmers.
        
        Query params:
            farmer_id: ID of the reference farmer
        """
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Avg, Q
        from farms.models import Farm
        
        User = get_user_model()
        farmer_id = request.query_params.get('farmer_id')
        
        if not farmer_id:
            return Response(
                {'error': 'farmer_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reference_farmer = User.objects.get(user_id=farmer_id, user_role='farmer')
        except User.DoesNotExist:
            return Response(
                {'error': 'Farmer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get reference farmer's locations (counties from their farms)
        reference_counties = set(
            Farm.objects.filter(farmer=reference_farmer)
            .values_list('sub_county__county_id', flat=True)
        )
        
        reference_sub_counties = set(
            Farm.objects.filter(farmer=reference_farmer)
            .values_list('sub_county_id', flat=True)
        )
        
        # Get reference farmer's product categories
        reference_categories = set(
            ProductListing.objects.filter(
                farmer=reference_farmer,
                listing_status__in=['available', 'pre_order']
            ).values_list('product__category_id', flat=True).distinct()
        )
        
        # Get all other farmers with active listings
        candidate_farmers = User.objects.filter(
            user_role='farmer',
            product_listings__listing_status__in=['available', 'pre_order']
        ).exclude(user_id=farmer_id).distinct()
        
        scored_farmers = []
        
        for farmer in candidate_farmers:
            score = 0
            
            # Get farmer's locations
            farmer_counties = set(
                Farm.objects.filter(farmer=farmer)
                .values_list('sub_county__county_id', flat=True)
            )
            farmer_sub_counties = set(
                Farm.objects.filter(farmer=farmer)
                .values_list('sub_county_id', flat=True)
            )
            
            # Location scoring
            # Same SubCounty: +10 points per match
            same_sub_counties = reference_sub_counties & farmer_sub_counties
            score += len(same_sub_counties) * 10
            
            # Same County: +5 points per match
            same_counties = reference_counties & farmer_counties
            score += len(same_counties) * 5
            
            # Get farmer's product categories
            farmer_categories = set(
                ProductListing.objects.filter(
                    farmer=farmer,
                    listing_status__in=['available', 'pre_order']
                ).values_list('product__category_id', flat=True).distinct()
            )
            
            # Category overlap: +3 points per shared category
            shared_categories = reference_categories & farmer_categories
            score += len(shared_categories) * 3
            
            # Get farmer rating
            try:
                from feedback.models import Review
                reviews = Review.objects.filter(
                    target_type='farmer',
                    target_id=farmer.user_id,
                    is_visible=True
                )
                avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
                review_count = reviews.count()
                
                # High rating bonus: +2 points if rating >= 4.0
                if avg_rating >= 4.0:
                    score += 2
            except:
                avg_rating = 0
                review_count = 0
            
            # Get active listings count
            active_listings = ProductListing.objects.filter(
                farmer=farmer,
                listing_status__in=['available', 'pre_order']
            ).count()
            
            # Only include farmers with a meaningful score or good rating
            if score > 0 or avg_rating >= 4.0:
                scored_farmers.append({
                    'farmer': farmer,
                    'score': score,
                    'avg_rating': avg_rating,
                    'review_count': review_count,
                    'active_listings': active_listings
                })
        
        # Sort by score (descending), then by rating
        scored_farmers.sort(key=lambda x: (-x['score'], -x['avg_rating']))
        
        # Take top 8 farmers
        top_farmers = scored_farmers[:8]
        
        related_farmers_data = []
        for item in top_farmers:
            farmer = item['farmer']
            
            # Get primary location
            primary_farm = Farm.objects.filter(farmer=farmer).first()
            primary_location = None
            if primary_farm:
                primary_location = f"{primary_farm.sub_county.county.county_name}"
            
            related_farmers_data.append({
                'farmer_id': farmer.user_id,
                'farmer_name': farmer.get_full_name(),
                'profile_photo_url': farmer.profile_photo_url,
                'average_rating': round(float(item['avg_rating']), 1) if item['avg_rating'] else 0.0,
                'review_count': item['review_count'],
                'active_listings_count': item['active_listings'],
                'primary_location': primary_location,
                'match_score': item['score']
            })
        
        return Response(related_farmers_data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def related_farms(self, request):
        """
        Get related farms based on location and product categories.
        Uses intelligent scoring algorithm to find the most relevant farms.
        
        Query params:
            farm_id: ID of the reference farm
        """
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Avg, Q
        from farms.models import Farm
        
        User = get_user_model()
        farm_id = request.query_params.get('farm_id')
        
        if not farm_id:
            return Response(
                {'error': 'farm_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reference_farm = Farm.objects.select_related('farmer', 'sub_county__county').get(farm_id=farm_id)
        except Farm.DoesNotExist:
            return Response(
                {'error': 'Farm not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get reference farm's product categories
        reference_categories = set(
            ProductListing.objects.filter(
                farm=reference_farm,
                listing_status__in=['available', 'pre_order']
            ).values_list('product__category_id', flat=True).distinct()
        )
        
        # Get all other farms with active listings
        candidate_farms = Farm.objects.filter(
            product_listings__listing_status__in=['available', 'pre_order']
        ).exclude(farm_id=farm_id).select_related('farmer', 'sub_county__county').distinct()
        
        scored_farms = []
        
        for farm in candidate_farms:
            score = 0
            
            # Location scoring
            # Same SubCounty: +10 points
            if farm.sub_county_id == reference_farm.sub_county_id:
                score += 10
            # Same County: +5 points
            elif farm.sub_county.county_id == reference_farm.sub_county.county_id:
                score += 5
            
            # Same weather zone: +3 points
            if farm.weather_zone == reference_farm.weather_zone:
                score += 3
            
            # Get farm's product categories
            farm_categories = set(
                ProductListing.objects.filter(
                    farm=farm,
                    listing_status__in=['available', 'pre_order']
                ).values_list('product__category_id', flat=True).distinct()
            )
            
            # Category overlap: +4 points per shared category
            shared_categories = reference_categories & farm_categories
            score += len(shared_categories) * 4
            
            # Both organic certified: +5 points
            if farm.is_certified_organic and reference_farm.is_certified_organic:
                score += 5
            
            # Get farmer rating
            try:
                from feedback.models import Review
                reviews = Review.objects.filter(
                    target_type='farmer',
                    target_id=farm.farmer.user_id,
                    is_visible=True
                )
                avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
                review_count = reviews.count()
                
                # High rating bonus: +2 points if rating >= 4.5
                if avg_rating >= 4.5:
                    score += 2
            except:
                avg_rating = 0
                review_count = 0
            
            # Get active products count
            active_products = ProductListing.objects.filter(
                farm=farm,
                listing_status__in=['available', 'pre_order']
            ).count()
            
            # Only include farms with a meaningful score
            if score > 0:
                scored_farms.append({
                    'farm': farm,
                    'score': score,
                    'avg_rating': avg_rating,
                    'review_count': review_count,
                    'active_products': active_products
                })
        
        # Sort by score (descending), then by rating
        scored_farms.sort(key=lambda x: (-x['score'], -x['avg_rating']))
        
        # Take top 8 farms
        top_farms = scored_farms[:8]
        
        related_farms_data = []
        for item in top_farms:
            farm = item['farm']
            
            related_farms_data.append({
                'farm_id': farm.farm_id,
                'farm_name': farm.farm_name,
                'farmer_id': farm.farmer.user_id,
                'farmer_name': farm.farmer.get_full_name(),
                'farmer_profile_photo': farm.farmer.profile_photo_url,
                'farmer_average_rating': round(float(item['avg_rating']), 1) if item['avg_rating'] else 0.0,
                'farmer_review_count': item['review_count'],
                'location': f"{farm.sub_county.sub_county_name}, {farm.sub_county.county.county_name}",
                'county': farm.sub_county.county.county_name,
                'is_certified_organic': farm.is_certified_organic,
                'farm_photos': farm.farm_photos if farm.farm_photos else [],
                'active_products_count': item['active_products'],
                'match_score': item['score']
            })
        
        return Response(related_farms_data)