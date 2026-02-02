from rest_framework import viewsets, mixins, permissions
from .models import Order
from .serializer import OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import OrderService



class OrderViewSet(viewsets.GenericViewSet, 
                   mixins.ListModelMixin, 
                   mixins.RetrieveModelMixin, 
                   mixins.CreateModelMixin):
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().select_related('address', 'user').prefetch_related('items__product__images')
        return Order.objects.filter(user=self.request.user).select_related('address').prefetch_related('items__product__images')
    
    
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_view(request):
    product_id = request.data.get('product_id')
    address_id = request.data.get('address_id')
    quantity = int(request.data.get('quantity', 1))

    try:
        order, client_secret = OrderService.create_order_with_payment(
            user=request.user,
            address_id=address_id,
            product_id=product_id,
            quantity=quantity
        )
        
        return Response({
            'order_id': order.id,
            'status': order.get_status_display(),
            'total_price': order.total_price,
            'client_secret': client_secret
        })

    except Exception as e:
        return Response({'error': str(e)}, status=400)