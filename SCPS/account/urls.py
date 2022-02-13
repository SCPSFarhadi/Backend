from django.urls import path ,include
from rest_framework_simplejwt import views as jwt_views
from .views import CustomTokenObtainPairView
urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]