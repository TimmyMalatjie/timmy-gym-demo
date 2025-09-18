# bookings/forms.py
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, time
from django.utils import timezone

from .models import Booking, Service
from accounts.models import TrainerProfile

class BookingForm(forms.ModelForm):
    """
    Create and edit bookings - like character creation form
    """
    
    class Meta:
        model = Booking
        fields = [
            'service', 
            'trainer', 
            'date', 
            'start_time', 
            'participants', 
            'special_requests'
        ]
        
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_service',
                'onchange': 'updateAvailableTimes()'
            }),
            'trainer': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_trainer'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_date',
                'onchange': 'updateAvailableTimes()',
                'min': timezone.now().date().isoformat()
            }),
            'start_time': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_start_time'
            }),
            'participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'value': 1
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests or notes for your trainer...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter active services only
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        
        # Filter available trainers
        self.fields['trainer'].queryset = TrainerProfile.objects.filter(
            is_accepting_clients=True
        )
        self.fields['trainer'].required = False
        
        # Set up time choices (9 AM to 8 PM)
        time_choices = [('', 'Select a time...')]
        for hour in range(9, 21):  # 9 AM to 8 PM
            time_obj = time(hour, 0)
            time_choices.append((
                time_obj.strftime('%H:%M'),
                time_obj.strftime('%I:%M %p')
            ))
        
        self.fields['start_time'].widget.choices = time_choices
        
        # Update field labels and help texts
        self.fields['service'].label = "Select Service"
        self.fields['service'].help_text = "Choose the type of training session"
        
        self.fields['trainer'].label = "Preferred Trainer (Optional)"
        self.fields['trainer'].help_text = "Leave blank for automatic assignment"
        
        self.fields['date'].label = "Preferred Date"
        self.fields['date'].help_text = "Choose your training date"
        
        self.fields['start_time'].label = "Preferred Time"
        self.fields['start_time'].help_text = "Available times will update based on your date selection"
        
        self.fields['participants'].label = "Number of Participants"
        self.fields['participants'].help_text = "How many people will attend? (Including yourself)"
        
        # If editing existing booking, set current values
        if self.instance and self.instance.pk:
            self.fields['start_time'].widget.attrs['data-current-time'] = self.instance.start_time.strftime('%H:%M')
    
    def clean_date(self):
        """Validate booking date"""
        date = self.cleaned_data.get('date')
        
        if not date:
            raise ValidationError("Please select a date.")
        
        # Don't allow booking in the past
        if date < timezone.now().date():
            raise ValidationError("Cannot book sessions in the past.")
        
        # Don't allow booking more than 60 days in advance
        max_advance_date = timezone.now().date() + timedelta(days=60)
        if date > max_advance_date:
            raise ValidationError("Cannot book more than 60 days in advance.")
        
        return date
    
    def clean_start_time(self):
        """Validate start time"""
        start_time = self.cleaned_data.get('start_time')
        
        if not start_time:
            raise ValidationError("Please select a start time.")
        
        # Convert string to time object if necessary
        if isinstance(start_time, str):
            try:
                start_time = datetime.strptime(start_time, '%H:%M').time()
            except ValueError:
                raise ValidationError("Invalid time format.")
        
        # Check if time is within business hours (9 AM to 8 PM)
        business_start = time(9, 0)
        business_end = time(20, 0)
        
        if start_time < business_start or start_time >= business_end:
            raise ValidationError("Sessions are only available between 9:00 AM and 8:00 PM.")
        
        return start_time
    
    def clean_participants(self):
        """Validate number of participants"""
        participants = self.cleaned_data.get('participants')
        service = self.cleaned_data.get('service')
        
        if participants and service:
            if participants > service.max_participants:
                raise ValidationError(
                    f"This service allows maximum {service.max_participants} participants."
                )
            
            if participants < 1:
                raise ValidationError("At least 1 participant is required.")
        
        return participants
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        trainer = cleaned_data.get('trainer')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        participants = cleaned_data.get('participants')
        
        if not all([service, date, start_time]):
            return cleaned_data
        
        # Check if user has membership requirement
        if service.requires_membership and self.user:
            if not hasattr(self.user, 'membership') or not self.user.membership.is_active:
                raise ValidationError(
                    f"{service.name} requires an active membership. Please purchase a membership first."
                )
        
        # Check for time conflicts (only for new bookings or when time changes)
        if self.user:
            existing_bookings = Booking.objects.filter(
                user=self.user,
                date=date,
                start_time=start_time,
                status__in=['pending', 'confirmed']
            )
            
            # Exclude current booking if editing
            if self.instance and self.instance.pk:
                existing_bookings = existing_bookings.exclude(pk=self.instance.pk)
            
            if existing_bookings.exists():
                raise ValidationError("You already have a booking at this time.")
        
        # Check service capacity
        existing_bookings_count = Booking.objects.filter(
            service=service,
            date=date,
            start_time=start_time,
            status__in=['pending', 'confirmed']
        )
        
        # Exclude current booking if editing
        if self.instance and self.instance.pk:
            existing_bookings_count = existing_bookings_count.exclude(pk=self.instance.pk)
        
        current_participants = sum(
            booking.participants for booking in existing_bookings_count
        )
        
        if current_participants + participants > service.max_participants:
            available_spots = service.max_participants - current_participants
            if available_spots <= 0:
                raise ValidationError("This time slot is fully booked.")
            else:
                raise ValidationError(
                    f"Only {available_spots} spots available at this time."
                )
        
        # Check trainer availability (if trainer selected)
        if trainer:
            trainer_bookings = Booking.objects.filter(
                trainer=trainer,
                date=date,
                start_time=start_time,
                status__in=['pending', 'confirmed']
            )
            
            # Exclude current booking if editing
            if self.instance and self.instance.pk:
                trainer_bookings = trainer_bookings.exclude(pk=self.instance.pk)
            
            if trainer_bookings.exists():
                raise ValidationError(
                    f"{trainer.user.get_full_name()} is not available at this time."
                )
        
        return cleaned_data

class BookingFilterForm(forms.Form):
    """
    Filter form for booking list view - like quest journal filters
    """
    STATUS_CHOICES = [
        ('all', 'All Bookings'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        required=False,
        empty_label="All Services",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class QuickBookingForm(forms.Form):
    """
    Simplified booking form for dashboard quick actions
    """
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    time = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up time choices
        time_choices = [('', 'Select a time...')]
        for hour in range(9, 21):
            time_obj = time(hour, 0)
            time_choices.append((
                time_obj.strftime('%H:%M'),
                time_obj.strftime('%I:%M %p')
            ))
        
        self.fields['time'].choices = time_choices