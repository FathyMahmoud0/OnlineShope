
from django.urls import path,include
from . import views

from rest_framework.routers import DefaultRouter
from .views import AddressViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    
    path('register/',views.register , name = 'register'),
    path('activate/',views.activate_account , name= "activate-account"),
    path('login/',views.user_login , name = 'login'),
    path('change_password/',views.change_password , name = 'change_password'),
    path('forget_password/',views.forgot_password, name = 'forget_password'),
    path('reset_password/', views.reset_password_confirm, name='reset-password'), 
    path('logout/', views.user_logout, name='logout'), 
    
    path('', include(router.urls)),

]