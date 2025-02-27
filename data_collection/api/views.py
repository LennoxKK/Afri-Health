import logging
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from geopy.geocoders import Nominatim
from .models import User, Category, Question, Option, Response as UserResponse
from .serializers import UserSerializer, QuestionSerializer
import assemblyai as aai

# Configure logging
logger = logging.getLogger(__name__)

# Set AssemblyAI API key
aai.settings.api_key = "bb9f8d48267b4a0e94cde53e9b0fcda8"  # Replace with your AssemblyAI API key

# Initialize geolocator
geolocator = Nominatim(user_agent="afri_health")

class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

class QuestionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Question.objects.all()
        category_name = self.request.query_params.get('category')
        if category_name:
            category = Category.objects.filter(name=category_name).first()
            if category:
                queryset = queryset.filter(category=category)
            else:
                queryset = queryset.none()
        return queryset

class AudioUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            logger.error("No audio file provided in the request")
            return Response({"error": "No audio file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Transcribe the audio file using AssemblyAI
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file)
            transcription_text = transcript.text
            logger.info("Audio file transcribed successfully using AssemblyAI")

            # Return the response with the transcribed text
            return Response({
                "message": "File uploaded and transcribed successfully",
                "transcribed_text": transcription_text,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            return Response({"error": f"Failed to process audio file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FrontEndData(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        try:
            if not data:
                return Response({"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            header_item = data[0]
            if not header_item:
                return Response({"error": "Invalid data format or missing header."}, status=status.HTTP_400_BAD_REQUEST)

            topic = header_item.get('topic')
            if not topic:
                return Response({"error": "Topic is required in the header."}, status=status.HTTP_400_BAD_REQUEST)

            category, _ = Category.objects.get_or_create(name=topic)
            location_data = header_item.get('location', {})
            lat = location_data.get('lat')
            lon = location_data.get('long')
            place_name = self._get_place_name(lat, lon)

            for item in data[1:]:
                answer_data = item.get('answer')
                if not answer_data:
                    continue

                question_text = answer_data.get('question')
                answer_text = answer_data.get('answer')
                if not question_text or not answer_text:
                    continue

                question = Question.objects.create(text=question_text, category=category)
                option = Option.objects.create(text=answer_text, question=question)
                UserResponse.objects.create(
                    user=user,
                    question=question,
                    selected_option=option,
                    location=place_name
                )

            return Response({"message": "Responses saved successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error saving responses: {str(e)}")
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_place_name(self, lat, lon):
        if not lat or not lon:
            return None

        try:
            location = geolocator.reverse((lat, lon), exactly_one=True)
            return location.address if location else None
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return None