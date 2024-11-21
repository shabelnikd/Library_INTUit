from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.RegistrationView.as_view()),
    path('activate/<str:activation_code>/', views.ActivationView.as_view()),
    path('login/', views.LoginView.as_view(), name="login"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', views.DetailsUserView.as_view()),
    path('reset_password/', views.ResetPasswordView.as_view()),
    path('reset_password_complete/', views.ResetPasswordCompleteView.as_view()),
    path('change_password/', views.ChangePasswordView.as_view()),
    path('info/<int:id>/', views.UserInfoView.as_view()),
    path('groups/', views.GroupListView.as_view()),
    path('stats/', views.UserStatsViewSet.as_view({'get': 'list'})),
    path('list/', views.UserList.as_view())

]
