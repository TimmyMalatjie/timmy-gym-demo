# bookings/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class Service(models.Model):
    """
    Different types of bookable services - like quest types
    """
    SERVICE_TYPES = [
        ('personal_training', 'Personal Training'),
        ('group_class', 'Group Class'),
        ('mma_session', 'MMA Training'),
        ('consultation', 'Fitness Consultation'),
        ('assessment', 'Fitness Assessment'),
    ]
    
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    max_participants = models.IntegerField(default=1)
    
    # Requirements
    requires_membership = models.BooleanField(default=True)
    minimum_fitness_level = models.CharField(max_length=20, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.duration_minutes}min - R{self.price})"

class Booking(models.Model):
    """
    Individual reservations - player's scheduled quests
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    trainer = models.ForeignKey('accounts.TrainerProfile', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Scheduling
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Booking Details
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    participants = models.IntegerField(default=1)
    special_requests = models.TextField(blank=True)
    
    # Payment
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.service.name} on {self.date}"
    
    def clean(self):
        # Validation logic
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
    
    @property
    def duration(self):
        return datetime.combine(self.date, self.end_time) - datetime.combine(self.date, self.start_time)