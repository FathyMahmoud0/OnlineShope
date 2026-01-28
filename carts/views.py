from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializer import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product__images')

    def list(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        existing_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            serializer.save(cart=cart)