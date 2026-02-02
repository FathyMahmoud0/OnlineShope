from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
from . import views , webhook

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('create/', views.create_order_view, name='create_order'),
    path('webhook/', webhook.stripe_webhook, name='stripe_webhook'),
]