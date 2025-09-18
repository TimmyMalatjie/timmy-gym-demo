# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, TrainerProfile

# Unregister the default User admin
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    """
    Inline profile editor for users
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        ('phone_number', 'date_of_birth', 'gender'),
        ('emergency_contact_name', 'emergency_contact_phone'),
        ('fitness_level', 'primary_goal'),
        'medical_conditions',
        'newsletter_subscription',
    )

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Enhanced user management with profiles
    """
    inlines = (UserProfileInline,)
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff',
        'date_joined'
    ]
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    """
    Control panel for trainer/staff management
    """
    list_display = [
        'user', 
        'specializations', 
        'years_experience', 
        'hourly_rate',
        'is_accepting_clients',
        'max_clients'
    ]
    list_filter = ['specializations', 'is_accepting_clients', 'years_experience']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'bio', 'profile_picture')
        }),
        ('Professional Details', {
            'fields': (
                'certifications', 
                'specializations', 
                'years_experience',
                'hourly_rate'
            )
        }),
        ('Availability', {
            'fields': ('is_accepting_clients', 'max_clients')
        }),
    )