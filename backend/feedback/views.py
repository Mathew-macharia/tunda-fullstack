from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewerOrAdminOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for the Review model"""
    queryset = Review.objects.filter(is_visible=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['target_type', 'target_id', 'rating', 'is_verified_purchase']
    search_fields = ['comment']
    ordering_fields = ['review_date', 'rating']
    ordering = ['-review_date']
    
    def get_queryset(self):
        """Filter reviews based on user role"""
        queryset = Review.objects.all()
        
        # Admin can see all reviews including invisible ones
        if self.request.user.is_authenticated and self.request.user.user_role == 'admin':
            return queryset
        
        # Non-admin users can only see visible reviews
        return queryset.filter(is_visible=True)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_reviews(self, request):
        """Return all reviews created by the current user"""
        reviews = Review.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def product_reviews(self, request):
        """Return all reviews for a specific product"""
        product_id = request.query_params.get('product_id', None)
        if product_id is None:
            return Response(
                {"detail": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.get_queryset().filter(target_type='product', target_id=product_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def farmer_reviews(self, request):
        """Return all reviews for a specific farmer"""
        farmer_id = request.query_params.get('farmer_id', None)
        if farmer_id is None:
            return Response(
                {"detail": "Farmer ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.get_queryset().filter(target_type='farmer', target_id=farmer_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def rider_reviews(self, request):
        """Return all reviews for a specific rider"""
        rider_id = request.query_params.get('rider_id', None)
        if rider_id is None:
            return Response(
                {"detail": "Rider ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.get_queryset().filter(target_type='rider', target_id=rider_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def moderate(self, request, pk=None):
        """Moderation endpoint for admins to update review visibility"""
        # Check if user is admin
        if request.user.user_role != 'admin':
            return Response({"detail": "Only admin users can moderate reviews"}, 
                            status=status.HTTP_403_FORBIDDEN)
        review = self.get_object()
        
        # Only update is_visible field
        is_visible = request.data.get('is_visible', None)
        if is_visible is None:
            return Response(
                {"detail": "is_visible field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review.is_visible = is_visible
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)
