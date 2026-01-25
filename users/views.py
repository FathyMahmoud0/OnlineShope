from .models import Address
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializer import RegistarSerializer,LoginSerializer , ChangePasswordSerializer ,ResetPasswordSerializer,PasswordResetConfirmSerializer , AddressSerializer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware import csrf
from .utils import generate_otp, send_activation_link, send_reset_password_link
from django.utils import timezone

from rest_framework import viewsets


User = get_user_model()

def get_tokens_for_user(user):
    
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegistarSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        try:
            send_activation_link(user, request)
        except Exception as e:
            print(f"Email sending failed: {e}")

        return Response(
            {"message": "User created. Please check your email to activate account."}, 
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])  
@permission_classes([AllowAny])
def activate_account(request):

    email = request.GET.get('email')
    otp = request.GET.get('otp')

    if not email or not otp:
        return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        
 
        if not user.is_active:
            if user.is_otp_valid(otp):
                user.is_active = True
                user.otp = None  
                user.save()
                
                return Response({"message": "Account activated successfully! You can login now."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Link is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        else:
             return Response({"message": "Account is already active."}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
            
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
 
    user = authenticate(request=request, username=email, password=password)
    
    if user is None:
        return Response(
            {"detail": "Invalid email or password."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    if  user.is_active is False:
        return Response(
            {"detail": "User account is disabled."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    tokens = get_tokens_for_user(user)

    response = Response()
    response.set_cookie(
        key='access_token',
        value=tokens['access'],
        httponly=True,
        secure=False, 
        samesite='Lax',
        max_age=30*60
    )

    response.data = {
        "message": "Login successful", 
        "user": user.email,
        "first_name" : user.first_name
    }
    
    response.status_code = status.HTTP_200_OK
    csrf.get_token(request) 

    return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        

        return Response(
            {"message": "Password updated successfully."}, 
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    
    serializer = ResetPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass        
        user.otp = generate_otp()
        user.otp_created_at = timezone.now()
        user.save()
        
        try:
            send_reset_password_link(user,request) 
        except Exception:
            return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    
    data = request.data.copy()

    if 'email' not in data:
        data['email'] = request.query_params.get('email')
        
    if 'otp' not in data:
        data['otp'] = request.query_params.get('otp')
        
    serializer = PasswordResetConfirmSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Password has been reset successfully. You can login now."}, status=status.HTTP_200_OK)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def user_logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception as e:
        pass

    response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    
    response.delete_cookie('access_token')

    return response



class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)