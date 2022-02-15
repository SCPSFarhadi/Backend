from django.urls import path ,include
from rest_framework_simplejwt import views as jwt_views
from .views import CustomTokenObtainPairView, CustomUserCreate

urlpatterns = [
    path('create/', CustomUserCreate.as_view(), name="create_user"),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]