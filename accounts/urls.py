from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication - using your actual view function names
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
        path('logout/', views.logout_view, name='logout'),
    
    # Profile management - using your actual view function names
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/complete/', views.profile_complete_view, name='profile_complete'),
    
    # Password management
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url='/accounts/dashboard/'
    ), name='password_change'),
]