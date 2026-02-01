from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.conf import settings
from .models import Review

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'products_count']
    
    def get_products_count(self, obj):
        return obj.products.count()

class ProductListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'slug', 
            'price', 
            'discount_price', 
            'final_price',
            'main_image', 
            'is_liked',        
            'in_stock'         
        ]

    def get_main_image(self, obj):
        img = obj.images.filter(is_main=True).first()
        if not img:
            img = obj.images.first()
        if img:
            return img.image.url
        return None

    def get_final_price(self, obj):
        if obj.discount_price and obj.discount_price < obj.price:
            return obj.discount_price
        return obj.price

    def get_is_liked(self, obj):
        # Personalization Logic
        user = self.context.get('request').user
        if user.is_authenticated:
            return False
        return False
    
    in_stock = serializers.BooleanField(source='is_active', read_only=True)



class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    similar_products = serializers.SerializerMethodField() 
    text_for_embedding = serializers.SerializerMethodField() 

    class Meta:
        model = Product
        fields = [
            'id', 
            'category', 
            'category_name',
            'name', 
            'slug', 
            'description', 
            'price', 
            'discount_price', 
            'stock', 
            'is_active', 
            'images',
            'similar_products',   
            'text_for_embedding'  
        ]

    def get_similar_products(self, obj):

        products = Product.objects.filter(category=obj.category).exclude(id=obj.id)[:4]
        return ProductListSerializer(products, many=True, context=self.context).data

    def get_text_for_embedding(self, obj):
        return f"{obj.name} {obj.description} {obj.category.name}"
    
    

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.IntegerField(source='total_likes', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'image', 'is_verified', 'likes_count', 'is_liked_by_user', 'created_at']
        read_only_fields = ['is_verified', 'product', 'user']

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False