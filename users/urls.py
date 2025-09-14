from django.urls import path
from .views import RegisterView, UserMeView, ChangePasswordView, MyFavoritesView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Profile & password
    path("me/", UserMeView.as_view(), name="user_me"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change_password"),

    # Favorites placeholder
    path("me/favorites/", MyFavoritesView.as_view(), name="user_favorites"),
]
