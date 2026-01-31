from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product, ProductImage
from .serializer import (
    CategorySerializer, 
    ProductListSerializer, 
    ProductDetailSerializer,
    ProductImageSerializer
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Product
from .serializer import ProductListSerializer
from .ai import AISearchEngine

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]
    
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def ai_search_view(request):
    query = request.query_params.get('q', None)
    category_id = request.query_params.get('category_id', None)
    min_price = request.query_params.get('min_price', None)
    max_price = request.query_params.get('max_price', None)

    if not query:
        return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        engine = AISearchEngine()
        product_ids = engine.search(query, k=10)

        products_queryset = Product.objects.filter(id__in=product_ids)

        if category_id:
            products_queryset = products_queryset.filter(category_id=category_id)

        if min_price:
            products_queryset = products_queryset.filter(price__gte=min_price)

        if max_price:
            products_queryset = products_queryset.filter(price__lte=max_price)

        products_dict = {p.id: p for p in products_queryset}
        sorted_products = [
            products_dict[pid] for pid in product_ids
            if pid in products_dict
        ]

        serializer = ProductListSerializer(
            sorted_products, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"ERROR: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)