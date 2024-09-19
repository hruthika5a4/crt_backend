from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import SubjectSerializer
class SubjectView(APIView):
    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')

        if email:
            
            try:
                # Find the user by email
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Fetch subjects associated with the user
            subjects = Subject.objects.filter(faculty_id=user)

            # Prepare the result dictionary
            result = {
                'email': email,
                'subjects': list(subjects.values('sub_id', 'name', 'class_id'))
            }

            return Response(result)

        subject_id = request.query_params.get('subject_id')

        if subject_id:
            
            try:
                # Fetch the subject object
                subject = Subject.objects.get(sub_id=subject_id)

                # Fetch the lesson plan associated with the subject
                lesson_plan = LessonPlan.objects.get(subject_id=subject)

                # Fetch all topics associated with the lesson plan
                topics = Topic.objects.filter(LessonPlan_id=lesson_plan)

                # Prepare the result dictionary
                result = {
                    'subject_id': subject_id,
                    'topics': list(topics.values('id', 'name', 'status', 'hours', 'target_date'))
                }

                return Response(result)
            except Subject.DoesNotExist:
                return Response({"error": "Subject not found"}, status=status.HTTP_404_NOT_FOUND)
            except LessonPlan.DoesNotExist:
                return Response({"error": "Lesson Plan not found for this subject"}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request, *args, **kwargs):
        serializer = SubjectSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # PATCH: Update an existing subject
    def patch(self, request, *args, **kwargs):
        sub_id = request.data.get('sub_id')
        
        if not sub_id:
            return Response(
                {"status": "error", "message": "Subject ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the subject object
        subject = get_object_or_404(Subject, sub_id=sub_id)
        
        # Partially update the subject
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Remove an existing subject
    def delete(self, request, *args, **kwargs):
        sub_id = request.GET.get('sub_id', None)
        
        if not sub_id:
            return Response(
                {"status": "error", "message": "Subject ID is required to delete"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the subject to delete
        subject = get_object_or_404(Subject, sub_id=sub_id)
        subject.delete()
        
        return Response({"status": "success", "message": "Subject deleted successfully"}, status=status.HTTP_200_OK)



class GetSubjectsByDepartment(APIView):
    def get(self, request, *args, **kwargs):
        dept = request.query_params.get('dept')

        if not dept:
            return Response({"error": "Department is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all subjects associated with the department
        subjects = Subject.objects.filter(class_id__dept=dept)

        # Prepare the result dictionary
        result = {
            'department': dept,
            'subjects': list(subjects.values('sub_id', 'name', 'faculty_id', 'class_id'))
        }

        return Response(result)
