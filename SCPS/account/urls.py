from django.urls import path ,include
from rest_framework_simplejwt import views as jwt_views
from .views import CustomTokenObtainPairView, CustomUserCreate, LogoutAPIView, MqttRunCommand, sendLastData, SetConfigNode

urlpatterns = [
    path('create/', CustomUserCreate.as_view(), name="create_user"),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('mqttrun/',MqttRunCommand.as_view()),
    path('sendlastdata/',sendLastData.as_view()),
    path('setnodeconfig/',SetConfigNode.as_view())
]