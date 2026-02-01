from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.chat_bot_view, name='chat_ask'),
    path('recommend/<int:product_id>/', views.smart_recommendation_view, name='ai_recommend'),
]