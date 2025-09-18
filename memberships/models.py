from django.db import models
from django.contrib.auth.models import User

class MembershipPlan(models.Model):
    """
    Subscription tiers - like game packages (Basic, Pro, Elite)
    """
    PLAN_TYPES = [
        ('basic', 'Basic Warrior'),
        ('premium', 'Elite Fighter'),
        ('vip', 'Champion Access'),
        ('corporate', 'Corporate Wellness'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2)
    setup_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Access permissions (what features this plan unlocks)
    gym_access = models.BooleanField(default=True)
    group_classes_included = models.IntegerField(default=0)  # 0 = unlimited
    personal_training_sessions = models.IntegerField(default=0)
    guest_passes = models.IntegerField(default=0)
    
    # Plan settings
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'monthly_price']
    
    def __str__(self):
        return f"{self.name} - R{self.monthly_price}/month"

class Membership(models.Model):
    """
    Player's active subscription - their current game pass
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    start_date = models.DateField()
    end_date = models.DateField()
    next_billing_date = models.DateField()
    
    # Usage tracking
    classes_used_this_month = models.IntegerField(default=0)
    pt_sessions_used_this_month = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name}"
    
    @property
    def is_active(self):
        return self.status == 'active'