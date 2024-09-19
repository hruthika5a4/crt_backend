from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import College
from .serializers import CollegeSerializer

class CollegeDetailsView(APIView):

    def get(self, request):
        id = request.data.get('id')
        if id:
            college = College.objects.get(id=id)
            serializer = CollegeSerializer(college)
            return Response(serializer.data)
        colleges = College.objects.all()
        serializer = CollegeSerializer(colleges, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CollegeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        id = request.data.get('id')
        if not id:
            return Response({"error": "id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        college = College.objects.get(id=id)
        serializer = CollegeSerializer(college, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.data.get('id')
        if not id:
            return Response({"error": "id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        college = College.objects.get(id=id)      
        college.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)