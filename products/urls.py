
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
    path('<int:product_id>/reviews/add/', views.add_review, name='add_review'),
    path('<int:product_id>/reviews/', views.get_product_reviews, name='get_reviews'),
    path('reviews/<int:review_id>/vote/', views.toggle_review_like, name='vote_review'),

]