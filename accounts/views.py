# accounts/views.py - UPDATED WITH REAL DATA
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count

from .forms import CustomUserRegistrationForm, UserProfileForm
from .models import UserProfile

def register_view(request):
    """
    Player registration controller - Character creation
    """
    if request.user.is_authenticated:
        messages.info(request, "You're already logged in!")
        return redirect('accounts:dashboard')

    
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            # Create the new player
            user = form.save()
            
            # Auto-login the new player
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(
                    request, 
                    f"Welcome to the elite, {user.first_name}! Your account has been created successfully."
                )
                return redirect('accounts:profile_complete')
            else:
                messages.error(request, "Account created but auto-login failed. Please try logging in manually.")
                return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_complete_view(request):
    """Simple profile completion that works"""
    # Get or create profile
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Just mark profile as complete and redirect
        messages.success(request, f"Welcome {request.user.first_name}! Your profile is complete.")
        return redirect('accounts:dashboard')
    
    # Show minimal form
    return render(request, 'accounts/profile_complete.html')

@login_required
def dashboard_view(request):
    """
    Player dashboard - Main game hub with real data
    """
    context = {
        'user': request.user,
    }
    
    # Get user's membership info
    try:
        membership = request.user.membership
        context['membership'] = membership
    except:
        context['membership'] = None
    
    # Get booking statistics
    try:
        from bookings.models import Booking
        
        # Get user's bookings
        user_bookings = Booking.objects.filter(user=request.user)
        
        # Next upcoming booking
        next_booking = user_bookings.filter(
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('date', 'start_time').first()
        context['next_booking'] = next_booking
        
        # Sessions this month
        current_month = timezone.now().month
        current_year = timezone.now().year
        sessions_this_month = user_bookings.filter(
            date__month=current_month,
            date__year=current_year,
            status='completed'
        ).count()
        context['sessions_this_month'] = sessions_this_month
        
        # Total completed sessions
        total_sessions = user_bookings.filter(status='completed').count()
        context['total_sessions'] = total_sessions
        
        # Progress calculation
        milestones = [5, 10, 20, 50, 100, 200, 500]
        next_milestone = next((m for m in milestones if m > total_sessions), 500)
        previous_milestone = max([m for m in milestones if m <= total_sessions] or [0])
        
        if next_milestone == 500 and total_sessions >= 500:
            progress_percentage = 100
        else:
            progress_range = next_milestone - previous_milestone
            progress_current = total_sessions - previous_milestone
            progress_percentage = int((progress_current / progress_range) * 100) if progress_range > 0 else 0
        
        context['progress_percentage'] = min(progress_percentage, 100)
        
        # Recent activity (last 5 bookings)
        recent_bookings = user_bookings.order_by('-date', '-start_time')[:5]
        context['recent_bookings'] = recent_bookings
        
        # Upcoming sessions (next 3)
        upcoming_bookings = user_bookings.filter(
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('date', 'start_time')[:3]
        context['upcoming_bookings'] = upcoming_bookings
        
    except ImportError:
        # Bookings app not available, use placeholder data
        context['next_booking'] = None
        context['sessions_this_month'] = 0
        context['total_sessions'] = 0
        context['progress_percentage'] = 0
        context['recent_bookings'] = []
        context['upcoming_bookings'] = []
    
    # Get user profile
    try:
        profile = request.user.userprofile
        context['profile'] = profile
        
        # Goal progress calculation
        if profile.primary_goal:
            goal_mapping = {
                'weight_loss': 16,      # 4 sessions per week
                'muscle_gain': 12,      # 3 sessions per week  
                'fitness': 8,           # 2 sessions per week
                'strength': 12,         # 3 sessions per week
                'endurance': 16,        # 4 sessions per week
                'mma': 12,              # 3 sessions per week
                'competition': 20,      # 5 sessions per week
            }
            
            monthly_target = goal_mapping.get(profile.primary_goal, 8)
            context['monthly_target'] = monthly_target
            
            monthly_progress = min(int((context['sessions_this_month'] / monthly_target) * 100), 100)
            context['monthly_progress'] = monthly_progress
            
            # Goal progress based on consistency
            try:
                weeks_active = user_bookings.filter(
                    date__gte=timezone.now().date() - timedelta(weeks=12),
                    status='completed'
                ).values('date__week').distinct().count()
                
                goal_progress = min(int((weeks_active / 12) * 100), 100)
                context['goal_progress'] = goal_progress
            except:
                context['goal_progress'] = min(context['sessions_this_month'] * 10, 100)
        else:
            context['monthly_target'] = 8
            context['monthly_progress'] = min(int((context['sessions_this_month'] / 8) * 100), 100)
            context['goal_progress'] = 0
            
    except UserProfile.DoesNotExist:
        context['profile'] = None
        context['monthly_target'] = 8
        context['monthly_progress'] = min(int((context['sessions_this_month'] / 8) * 100), 100)
        context['goal_progress'] = 0
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    """
    Profile management - Character sheet editor
    """
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

def custom_logout_view(request):
    """
    Custom logout with personalized message
    """
    if request.user.is_authenticated:
        username = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f"See you later, {username}! Keep crushing those goals!")
    
    return render(request, 'registration/logged_out.html')

def logout_view(request):
    # Get the user's name BEFORE logging them out
    if request.user.is_authenticated:
        user_first_name = request.user.first_name or "Champion"
    else:
        user_first_name = "Champion"
    
    # Now perform the logout
    logout(request)
    
    # Add personalized message using the name we captured
    messages.success(request, f"Thanks for training with us today, {user_first_name}! Your session has been logged out securely.")
    
    return redirect('accounts:login')