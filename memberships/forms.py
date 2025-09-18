from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from .models import MembershipPlan, Membership

class MembershipPurchaseForm(forms.Form):
    """
    Membership purchase form - like character upgrade selection
    """
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', '3 Months (5% discount)'),
        ('annually', '12 Months (10% discount)'),
    ]
    
    start_immediately = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Start membership immediately",
        help_text="Uncheck to schedule start for a future date"
    )
    
    billing_cycle = forms.ChoiceField(
        choices=BILLING_CYCLE_CHOICES,
        initial='monthly',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Billing Cycle"
    )
    
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I agree to the Terms of Service and Privacy Policy",
        error_messages={'required': 'You must agree to the terms to continue.'}
    )
    
    marketing_emails = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Send me workout tips, gym news, and special offers",
        help_text="You can unsubscribe at any time"
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.plan = kwargs.pop('plan', None)
        super().__init__(*args, **kwargs)
        
        if self.plan:
            # Convert discount percentages to Decimal for proper calculation
            quarterly_discount = Decimal('0.95')  # 5% discount
            annually_discount = Decimal('0.90')   # 10% discount
            
            # Calculate prices using Decimal arithmetic
            monthly_price = self.plan.monthly_price
            quarterly_total = monthly_price * 3 * quarterly_discount
            annually_total = monthly_price * 12 * annually_discount
            
            # Update billing cycle choices with actual prices
            self.fields['billing_cycle'].choices = [
                ('monthly', f'Monthly (R{monthly_price}/month)'),
                ('quarterly', f'3 Months (R{quarterly_total:.0f} total - 5% discount)'),
                ('annually', f'12 Months (R{annually_total:.0f} total - 10% discount)'),
            ]
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if user already has active membership
        if self.user:
            try:
                existing_membership = Membership.objects.get(user=self.user)
                if existing_membership.is_active:
                    raise ValidationError(
                        "You already have an active membership. Please cancel your current membership before purchasing a new one."
                    )
            except Membership.DoesNotExist:
                pass
        
        return cleaned_data

class BillingInfoForm(forms.Form):
    """
    Mock payment form - like in-game purchase screen
    For demo purposes only - do not use in production
    """
    # Personal Information
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name as on Card'
        }),
        label="Cardholder Name"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        label="Email Address"
    )
    
    # Mock Credit Card Information
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '4111 1111 1111 1111',
            'data-mask': '0000 0000 0000 0000'
        }),
        label="Card Number",
        help_text="Use 4111-1111-1111-1111 for demo success, 4000-0000-0000-0000 for demo failure"
    )
    
    expiry_month = forms.ChoiceField(
        choices=[(i, f'{i:02d}') for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Expiry Month"
    )
    
    expiry_year = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(datetime.now().year, datetime.now().year + 10)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Expiry Year"
    )
    
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'maxlength': '4'
        }),
        label="CVV/CVC"
    )
    
    # Billing Address
    address_line1 = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123 Main Street'
        }),
        label="Address Line 1"
    )
    
    address_line2 = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apartment, suite, etc. (optional)'
        }),
        label="Address Line 2"
    )
    
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Johannesburg'
        }),
        label="City"
    )
    
    province = forms.ChoiceField(
        choices=[
            ('GP', 'Gauteng'),
            ('WC', 'Western Cape'),
            ('KZN', 'KwaZulu-Natal'),
            ('EC', 'Eastern Cape'),
            ('FS', 'Free State'),
            ('LP', 'Limpopo'),
            ('MP', 'Mpumalanga'),
            ('NC', 'Northern Cape'),
            ('NW', 'North West'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Province"
    )
    
    postal_code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '2000'
        }),
        label="Postal Code"
    )
    
    def clean_card_number(self):
        """Validate card number (mock validation)"""
        card_number = self.cleaned_data.get('card_number', '').replace(' ', '')
        
        if len(card_number) < 13 or len(card_number) > 19:
            raise ValidationError("Invalid card number length.")
        
        if not card_number.isdigit():
            raise ValidationError("Card number should contain only digits.")
        
        return card_number
    
    def clean_cvv(self):
        """Validate CVV"""
        cvv = self.cleaned_data.get('cvv', '')
        
        if len(cvv) < 3 or len(cvv) > 4:
            raise ValidationError("CVV must be 3 or 4 digits.")
        
        if not cvv.isdigit():
            raise ValidationError("CVV should contain only digits.")
        
        return cvv
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        expiry_month = cleaned_data.get('expiry_month')
        expiry_year = cleaned_data.get('expiry_year')
        
        if expiry_month and expiry_year:
            expiry_date = datetime(int(expiry_year), int(expiry_month), 1)
            if expiry_date < datetime.now():
                raise ValidationError("Card has expired.")
        
        return cleaned_data

class MembershipUpgradeForm(forms.Form):
    """
    Membership upgrade form - character class upgrade
    """
    new_plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Select New Plan"
    )
    
    upgrade_immediately = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Upgrade immediately",
        help_text="Prorated charges will apply"
    )
    
    def __init__(self, *args, **kwargs):
        self.current_membership = kwargs.pop('current_membership', None)
        super().__init__(*args, **kwargs)
        
        if self.current_membership:
            # Only show plans that are upgrades (higher price)
            self.fields['new_plan'].queryset = MembershipPlan.objects.filter(
                is_active=True,
                monthly_price__gt=self.current_membership.plan.monthly_price
            ).order_by('monthly_price')
    
    def clean_new_plan(self):
        new_plan = self.cleaned_data.get('new_plan')
        
        if self.current_membership and new_plan:
            if new_plan.monthly_price <= self.current_membership.plan.monthly_price:
                raise ValidationError("You can only upgrade to a higher-tier plan.")
        
        return new_plan

class MembershipCancelForm(forms.Form):
    """
    Membership cancellation form - unsubscribe flow
    """
    CANCELLATION_REASONS = [
        ('too_expensive', 'Too expensive'),
        ('not_using', 'Not using enough'),
        ('moving', 'Moving away'),
        ('health_issues', 'Health issues'),
        ('schedule_change', 'Schedule changed'),
        ('dissatisfied', 'Dissatisfied with service'),
        ('other', 'Other reason'),
    ]
    
    reason = forms.ChoiceField(
        choices=CANCELLATION_REASONS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Reason for cancellation"
    )
    
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Help us improve by sharing your feedback...'
        }),
        label="Additional Feedback (Optional)"
    )
    
    confirm_cancellation = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I understand that cancelling will end my membership benefits",
        error_messages={'required': 'You must confirm to proceed with cancellation.'}
    )

class QuickMembershipForm(forms.Form):
    """
    Simplified membership selection for dashboard or popups
    """
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        empty_label="Choose Your Plan...",
        label="Select Membership Plan"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize plan display
        plan_choices = []
        for plan in MembershipPlan.objects.filter(is_active=True).order_by('sort_order'):
            plan_choices.append((
                plan.id, 
                f"{plan.name} - R{plan.monthly_price}/month"
            ))
        
        self.fields['plan'].choices = [('', 'Choose Your Plan...')] + plan_choices

class MembershipGiftForm(forms.Form):
    """
    Gift membership form - buy for someone else
    """
    recipient_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'recipient@example.com'
        }),
        label="Recipient's Email"
    )
    
    recipient_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Recipient\'s Full Name'
        }),
        label="Recipient's Name"
    )
    
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Gift Plan"
    )
    
    gift_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Personal message for the recipient...'
        }),
        label="Gift Message (Optional)"
    )
    
    send_immediately = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Send gift immediately",
        help_text="Uncheck to schedule for a specific date"
    )

class ProfileUpdateForm(forms.ModelForm):
    """
    Update user profile during membership purchase
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+27 12 345 6789'
        }),
        label="Phone Number"
    )
    
    emergency_contact_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Emergency contact name'
        }),
        label="Emergency Contact Name"
    )
    
    emergency_contact_phone = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+27 12 345 6789'
        }),
        label="Emergency Contact Phone"
    )