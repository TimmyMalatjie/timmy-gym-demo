# memberships/admin.py
from django.contrib import admin
from .models import MembershipPlan, Membership

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    """
    Control panel for membership packages
    """
    list_display = [
        'name', 
        'plan_type', 
        'monthly_price', 
        'gym_access', 
        'group_classes_included',
        'is_active'
    ]
    list_filter = ['plan_type', 'is_active', 'gym_access']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'monthly_price']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'plan_type', 'description')
        }),
        ('Pricing', {
            'fields': ('monthly_price', 'setup_fee')
        }),
        ('Access Permissions', {
            'fields': (
                'gym_access', 
                'group_classes_included', 
                'personal_training_sessions',
                'guest_passes'
            )
        }),
        ('Settings', {
            'fields': ('is_active', 'sort_order')
        }),
    )

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """
    Control panel for active player subscriptions
    """
    list_display = [
        'user', 
        'plan', 
        'status', 
        'start_date', 
        'end_date',
        'classes_used_this_month'
    ]
    list_filter = ['status', 'plan', 'start_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Member Info', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Subscription Period', {
            'fields': ('start_date', 'end_date', 'next_billing_date')
        }),
        ('Usage Tracking', {
            'fields': ('classes_used_this_month', 'pt_sessions_used_this_month')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing membership
            return ['user', 'created_at']
        return ['created_at']