from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import generate_otp 
from django.utils import timezone

User = get_user_model()
    

class RegistarSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length=60, min_length=8,write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=60, min_length=8,write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name','email', 'password','confirm_password']
        read_only_fields = ['username']
        extra_kwargs = {
            'email': {'required': True},
        }
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError("Password and confirmation password do not match.")
            
        data.pop('confirm_password')
        return data
        
    def create(self , validated_data):
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email'].split('@')[0]
            
        user = User.objects.create_user(
                first_name = validated_data['first_name'],
                last_name = validated_data['last_name'],
                email = validated_data['email'],
                username = validated_data['username'],
                password = validated_data['password']
            )
        
        user.is_active = False
        user.otp = generate_otp()  
        user.otp_created_at = timezone.now()
        
        user.save()
        
        return user
    
class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField(max_length=60,write_only=True, required=True)
    password = serializers.CharField(max_length=60,write_only=True, required=True)



class ChangePasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_new_password = serializers.CharField(required=True, min_length=8, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("the old password not correct")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
             raise serializers.ValidationError({"confirm_new_password":"the new password and confirm password are not correct"})
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
class ResetPasswordSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("User with this email does not exist.")
        return value
    
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise ValidationError({"password": "Passwords do not match."})

        email = data['email']
        otp = data['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError({"email": "User not found."})

        if not user.is_otp_valid(otp):
            raise ValidationError({"otp": "Invalid or expired OTP."})

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        user.set_password(new_password)
        user.otp = None 
        user.save()
        return user


