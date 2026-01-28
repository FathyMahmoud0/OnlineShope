from rest_framework import viewsets, mixins, permissions
from .models import Order
from .serializer import OrderSerializer

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