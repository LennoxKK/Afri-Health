from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.parsers import JSONParser

# class DataReceivingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         print(f"Raw data: {request.body}")  # Debugging raw request payload
#         try:
#             print(f"Parsed JSON data: {request.data}")  # Debugging parsed request data
#             data = request.data.get('data')
#             print(f"Extracted data: {data}")
#             print(f"Authenticated user: {request.user}")
#         except Exception as e:
#             print(f"Error while accessing data: {e}")
#         return Response({'message': 'Data received successfully'}, status=200)
    
#     # views.py

# In views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, status, serializers
from data_collection.models import User  # Ensure the custom User model is imported
from .serializers import UserSerializer

class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication to access this endpoint
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()  # Return all users

from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from .serializers import QuestionSerializer
from .models import Question, Category

class QuestionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication to access this endpoint
    serializer_class = QuestionSerializer
    pagination_class = PageNumberPagination  # Add pagination for large datasets

    def get_queryset(self):
        # Get all questions by default
        queryset = Question.objects.all()
        print(queryset)

        # Filter based on query parameters (e.g., category)
        category_name = self.request.query_params.get('category', None)
        if category_name:
            # Get the category object from the name, and filter questions by category
            category = Category.objects.filter(name=category_name).first()
            if category:
                queryset = queryset.filter(category=category)
            else:
                queryset = queryset.none()  # No questions if category is not found
        print(queryset)
        return queryset

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from geopy.geocoders import Nominatim
from .models import Category, Question, Option, Response as UserResponse



class FrontEndData(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # print((data))
        user = request.user
        geolocator = Nominatim(user_agent="afri_health")
        
        try:
            COUNT_ITEM = 0
            HEADER_ITEM = []
            for item in data:
                # Validate data format
                if COUNT_ITEM == 0:
                    # Get the header
                    HEADER_ITEM.append(item)
                    COUNT_ITEM =1
                if item not in HEADER_ITEM:
                    if not HEADER_ITEM[0].get('topic') or not item.get('answer') or not item['answer'].get('question') or not item['answer'].get('answer'):
                        return Response({"error": "Invalid data format or missing fields."}, status=status.HTTP_400_BAD_REQUEST)

                    # Geolocation handling
                    location_data = HEADER_ITEM[0].get('location', {})
                    if not isinstance(location_data, dict):
                        location_data = {}  # Ensure it's a dictionary

                    lat = location_data.get('lat')
                    lon = location_data.get('long')
                    
                    place_name = None

                    try:
                        if lat and lon:
                            location = geolocator.reverse((lat, lon), exactly_one=True)
                            place_name = location.address if location else None
                    except Exception as geocode_error:
                        place_name = None  # Default to None if geocoding fails
                        print(f"Geocoding error: {geocode_error}")

                    # Create models directly
                    topic = HEADER_ITEM[0]['topic']
                    category, _ = Category.objects.get_or_create(name=topic)
                    answer_data = item['answer']
                    question_text = answer_data['question']
                    question = Question.objects.create(text=question_text, category=category)
                    answer_text = answer_data['answer']
                    option = Option.objects.create(text=answer_text, question=question)

                    # Save user response
                    UserResponse.objects.create(
                        user=user,
                        question=question,
                        selected_option=option,
                        location=place_name
                    )
                
            
            return Response({"message": "Responses saved successfully."}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
