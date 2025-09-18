from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    """
    Extended player profile - their character sheet
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    FITNESS_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('athlete', 'Professional Athlete'),
    ]
    
    GOALS = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('fitness', 'General Fitness'),
        ('strength', 'Strength Training'),
        ('endurance', 'Endurance'),
        ('mma', 'MMA Training'),
        ('competition', 'Competition Prep'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Personal Info
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Fitness Profile
    fitness_level = models.CharField(max_length=20, choices=FITNESS_LEVELS, default='beginner')
    primary_goal = models.CharField(max_length=20, choices=GOALS, blank=True)
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions or injuries")
    
    # Preferences
    preferred_training_time = models.CharField(max_length=50, blank=True)
    newsletter_subscription = models.BooleanField(default=True)
    
    # Profile Settings
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
    
    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class TrainerProfile(models.Model):
    """
    Staff/Trainer character sheets - for the gym team
    """
    SPECIALIZATIONS = [
        ('personal_training', 'Personal Training'),
        ('mma', 'MMA Coaching'),
        ('boxing', 'Boxing'),
        ('strength', 'Strength & Conditioning'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('nutrition', 'Nutrition Coaching'),
        ('physiotherapy', 'Physiotherapy'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Professional Info
    certifications = models.TextField(help_text="List of certifications and qualifications")
    specializations = models.CharField(max_length=100, choices=SPECIALIZATIONS)
    years_experience = models.IntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Availability
    is_accepting_clients = models.BooleanField(default=True)
    max_clients = models.IntegerField(default=20)
    
    # Profile
    bio = models.TextField(max_length=1000)
    profile_picture = models.ImageField(upload_to='trainers/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Trainer: {self.user.get_full_name()}"