
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import UserListView,FrontEndData,QuestionListView,AudioUploadView
app_name = "data-api"  
urlpatterns = [
        path('upload/', AudioUploadView.as_view(), name='audio-upload'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='data-api:schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='data-api:schema'), name='redoc'),
    
    # path('front-end-data/', DataReceivingView.as_view(), name='front-end-data'),
     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('front-end-data/', FrontEndData.as_view(), name='front-end-data'),
]