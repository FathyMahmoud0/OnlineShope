
from django.urls import path,include
from . import views

from rest_framework.routers import DefaultRouter
from .views import AddressViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    
    path(r'register/',views.register , name = 'register'),
    path(r'activate/',views.activate_account , name= "activate-account"),
    path(r'login/',views.user_login , name = 'login'),
    path(r'change_password/',views.change_password , name = 'change_password'),
    path(r'forget_password/',views.forgot_password, name = 'forget_password'),
    path(r'reset_password/', views.reset_password_confirm, name='reset-password'), 
    path(r'logout/', views.user_logout, name='logout'), 
    
    path('', include(router.urls)),

]