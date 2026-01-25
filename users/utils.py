from django.core.mail import send_mail
from django.conf import settings
import random
from django.urls import reverse

def generate_otp():

    return str(random.randint(100000, 999999))

def send_activation_link(user, request):

    current_site = request.get_host()
    
    relative_link = reverse('activate-account') 

    activation_link = f"http://{current_site}{relative_link}?email={user.email}&otp={user.otp}"

    # 2. تجهيز الإيميل
    subject = 'Activate your account'
    message = f'Hi {user.first_name},\nPlease click the link below to activate your account:\n{activation_link}'
    
    # 3. الإرسال
    send_mail(
        subject, 
        message, 
        settings.EMAIL_HOST_USER, 
        [user.email], 
        fail_silently=False
    )
    
def send_reset_password_link(user, request):

    current_site = request.get_host()
    

    relative_link = reverse('reset-password') 
    
    reset_link = f"http://{current_site}{relative_link}?email={user.email}&otp={user.otp}"

    subject = 'Reset Your Password'
    message = f'Hi {user.first_name},\nClick the link below to reset your password:\n{reset_link}\n\n(Copy the parameters from this link to set your new password)'
    
    send_mail(
        subject, 
        message, 
        settings.EMAIL_HOST_USER, 
        [user.email], 
        fail_silently=False
    )