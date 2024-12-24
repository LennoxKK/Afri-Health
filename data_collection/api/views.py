from rest_framework.views import APIView
from rest_framework.response import Response
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
            HEADER_ITEM =None
            for item in data:
                # Validate data format
                if HEADER_ITEM== None:
                    # Get the header
                    HEADER_ITEM =item
                if item != HEADER_ITEM:
                    if not HEADER_ITEM.get('topic') or not item.get('answer') or not item['answer'].get('question') or not item['answer'].get('answer'):
                        return Response({"error": "Invalid data format or missing fields."}, status=status.HTTP_400_BAD_REQUEST)

                    # Geolocation handling
                    location_data = HEADER_ITEM.get('location', {})
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
                    topic = HEADER_ITEM['topic']
                    category, _ = Category.objects.get_or_create(name=topic)
                    answer_data = item['answer']
                    question_text = answer_data['question']
                    question = Question.objects.create(text=question_text, category=category)
                    answer_text = answer_data['answer']
                    option = Option.objects.create(text=answer_text, question=question)
                    print(item)
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
