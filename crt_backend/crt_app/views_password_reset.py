from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework import status
import smtplib
from django.core.exceptions import ValidationError
import random
import string



def generate_reset_code():
        code = ''.join(random.choices(string.digits, k=6))
        return code

def send_reset_email(email, reset_code):
        # Send an email with the reset code using smtplib
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("crtproject258@gmail.com", "lxiz muyd zast abwg")
        subject = "Password Reset Code"
        message = f"Subject: {subject}\n\nYour password reset code is {reset_code}. Please enter this code to reset your password."
        server.sendmail("crtproject258@gmail.com", "hruthika.sa258@gmail.com", message)
        server.quit()

def request_password_reset( email):
        # Generate and send reset code
        
        try:
                
            user = User.objects.get(email=email)
            print(user)
        except User.DoesNotExist:
            raise ValidationError("No user with this email address exists.")
        sent=False
        reset_code = generate_reset_code()
        user.reset_password = reset_code
        try:
            send_reset_email(email, reset_code)
            user.save()

        except:
            pass
        else:
            sent=True
        if sent:
            return "Reset code sent to email."
        else:
            raise ValidationError(" email is not sent Please try again.")

def validate_reset_code( email, entered_code):
        print("enetred code")
        # Validate the entered reset code
        valid=False
        # print(user,user.reset_password)
        try:
            user = User.objects.get(email=email)
            print(user,user.reset_password)
            if user.reset_password == entered_code:
            
                valid=True
        except User.DoesNotExist:
            pass
        return valid

def reset_password( email, new_password):
        # Reset password if the code is valid
        if email:
            user = User.objects.get(email=email)
            user.password=new_password 
            user.reset_password=""
            user.save()
            
            return "Password successfully reset."
        else:
            raise ValidationError("Invalid reset code or code expired.")

class PasswordResetView(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        if email:
            try:
                message = request_password_reset(email)
                return Response({"message": message}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        new_password = request.data.get('new_password')
        email = request.data.get('email')
        reset_code = request.data.get('reset_code')
        print(reset_code,email)
        if email and reset_code:
            if validate_reset_code(email, reset_code):
                try:
                    message = reset_password(email, new_password)
                except Exception as e:
                    return Response({"error:",str(e)}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"message": "Try new password to login."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid reset code."}, status=status.HTTP_200_OK)
        return Response({"error": "Email and reset code are required."}, status=status.HTTP_400_BAD_REQUEST)
