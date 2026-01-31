
from django.urls import path,include
from . import views

from rest_framework.routers import DefaultRouter
from .views import ProductViewSet , CategoryViewSet ,ProductImageViewSet

router = DefaultRouter()

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'images', ProductImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ai_search/', views.ai_search_view, name='ai-search'),
]