from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework import status
import smtplib


def sendmail(stu_name,approval_type,old_data,new_data):
    server =smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login("crtproject258@gmail.com","lxiz muyd zast abwg")
    message=stu_name + " has sent a apprval request with type "+approval_type+" changing from "+old_data+" to "+new_data
    server.sendmail("crtproject258@gmail.com","hruthika.sa258@gmail.com",message)
    print("hi")

def sendmail_response(stu_name,approval_type,old_data,new_data):
    server =smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login("crtproject258@gmail.com","lxiz muyd zast abwg")
    message=stu_name + " has approved request with type "+approval_type+" changing from "+old_data+" to "+new_data
    server.sendmail("crtproject258@gmail.com","hruthika.sa258@gmail.com",message)
    print("hi")


class ApprovalView(APIView):
    def get(self, request, *args, **kwargs):
        approval_id = request.query_params.get('approval_id')
        
        if not approval_id:
            return Response({"error": "Approval ID is required"}, status=400)

        try:
            approval = Approval.objects.get(approval_id=approval_id)
        except Approval.DoesNotExist:
            return Response({"error": "Approval not found"}, status=404)

        # Prepare the result dictionary
        result = {
            'approval_id': approval.approval_id,
            'user_name': approval.user_name,
            'roll_number': approval.roll_number,
            'user_email': approval.user_email,
            'hod_id': approval.hod_id.id,
            'dept': approval.dept,
            'status': approval.status,
            'approval_type': approval.approval_type,
            'old_data': approval.old_data,
            'new_data': approval.new_data
        }

        return Response(result)



    def patch(self, request):
        action = request.data.get('status')
        approval_id = request.data.get('approval_id')
        
        print(action,approval_id)
        if not action or not approval_id:
            return Response({'error': 'Action and approval_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            approval = Approval.objects.get(approval_id=approval_id)
            # Retrieve details from the approval record
            user_email = approval.user_email
            approval_type = approval.approval_type
            old_data = approval.old_data
            new_data = approval.new_data
            user_name=approval.user_name
            # Retrieve the associated user
            user = User.objects.get(email=user_email)
            
            if action == 'approved':
                if approval_type == 'new_stu_account':
                        print("12345")
                        user.status = 'AC'
                        user.save(update_fields=['status'])
                # elif approval_type == 'percentage':
                #     user.percentage = int(new_data) 
                #     user.save(update_fields=['percentage'])
                elif approval_type == 'new_fac_account':
                        print("dwwr")
                        user.status = 'AC'
                        user.save(update_fields=['status'])         
                # elif approval_type == 'new_lessonplan_approval':
                #     lsp=LessonPlan.objects.get()
                #     LessonPlan.status = 'AC'
                #     user.save(update_fields=['college_name'])
                approval.status = 'approved'
                approval.save()
                print(user_name,approval_type,old_data,new_data)
                sendmail_response(user_name,approval_type,old_data,new_data)
                return Response({'message': 'Approval accepted and user updated successfully.'}, status=status.HTTP_200_OK)        
            elif action == 'rejected':
                approval.status = 'Rejected'
                approval.save()
                sendmail_response(user.first_name,approval_type,old_data,new_data)
                return Response({'message': 'Approval rejected successfully.'}, status=status.HTTP_200_OK)
        
            else:
                return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        except Approval.DoesNotExist:
            return Response({'error': 'Approval record not found.'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    
    
    def delete(self, request, *args, **kwargs):
        approval_id = request.query_params.get('approval_id')
        
        if not approval_id:
            return Response({"error": "Approval ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            approval = Approval.objects.get(approval_id=approval_id)
            approval.delete()
            return Response({"message": "Approval deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Approval.DoesNotExist:
            return Response({"error": "Approval not found"}, status=status.HTTP_404_NOT_FOUND)    

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
