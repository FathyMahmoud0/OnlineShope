from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
from django.utils import timezone
from datetime import timedelta



class UserManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('email not found')
        if not username:
            raise ValueError('username not found')
        
        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            username = username,
        )
        
        user.set_password(password)
        user.save(using = self._db)
        
        return user

    def create_superuser(self,first_name,last_name,username,email,password=None):
        
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            username = username,
            password=password,
        )
        
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.is_admin  = True
        
        user.save(using = self._db)
        return user

class CustomUser(AbstractBaseUser):
    
    email = models.EmailField(unique=True , max_length=30)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(unique=True,max_length=30)
    phone_number = models.CharField(max_length=11,unique=True,null=True,blank=True)
    image = models.ImageField(upload_to='photos/',blank=True,null=True)
    
    
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username' , 'first_name' , 'last_name']
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser
    
    def has_module_perms(self, app_label):

        return self.is_active and self.is_staff
    
    def is_otp_valid(self, input_otp):
        if self.otp is None:
            return False
        expiry_time = self.otp_created_at + timedelta(minutes=10)
        return self.otp == input_otp and timezone.now() < expiry_time
    

    
