# bookings/admin.py
from django.contrib import admin
from .models import Service, Booking

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Control panel for bookable services
    """
    list_display = [
        'name', 
        'service_type', 
        'duration_minutes', 
        'price',
        'max_participants',
        'is_active'
    ]
    list_filter = ['service_type', 'is_active', 'requires_membership']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'service_type', 'description')
        }),
        ('Duration & Pricing', {
            'fields': ('duration_minutes', 'price', 'max_participants')
        }),
        ('Requirements', {
            'fields': ('requires_membership', 'minimum_fitness_level')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Control panel for managing reservations
    """
    list_display = [
        'user', 
        'service', 
        'trainer',
        'date', 
        'start_time',
        'status',
        'payment_status'
    ]
    list_filter = [
        'status', 
        'payment_status', 
        'service__service_type',
        'date'
    ]
    search_fields = [
        'user__username', 
        'user__first_name', 
        'user__last_name',
        'service__name'
    ]
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('user', 'service', 'trainer')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'participants')
        }),
        ('Status & Payment', {
            'fields': ('status', 'amount_paid', 'payment_status')
        }),
        ('Additional Info', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing booking
            return ['created_at']
        return ['created_at']