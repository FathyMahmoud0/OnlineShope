from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from carts.models import Cart
from products.models import Product
from products.serializer import ProductListSerializer
from users.models import Address

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'created_at', 'address_id', 'items']
        read_only_fields = ['total_price', 'status']

    # 3. دالة التحقق لمنع الـ 500 Error
    def validate(self, attrs):
        user = self.context['request'].user
        address_id = attrs.get('address_id')
        
        # نتأكد أن العنوان موجود + أنه ملك لهذا المستخدم
        if not Address.objects.filter(id=address_id, user=user).exists():
            raise serializers.ValidationError({
                "address_id": "Invalid address ID. Please check if the address exists and belongs to you."
            })
            
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        address_id = validated_data['address_id']
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart is empty.")

        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                address_id=address_id,
                total_price=cart.total_price
            )

            order_items = []
            # استخدام select_related لتحسين الأداء
            for item in cart.items.select_related('product'):
                if item.quantity > item.product.stock:
                    raise serializers.ValidationError(f"Not enough stock for {item.product.name}")

                item.product.stock -= item.quantity
                item.product.save()

                price = item.product.discount_price if item.product.discount_price else item.product.price

                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=price
                    )
                )

            OrderItem.objects.bulk_create(order_items)
            cart.items.all().delete()
            
            return order