# core/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite

# Custom admin site configuration
admin.site.site_header = "Timmy's Elite Performance Center"
admin.site.site_title = "Timmy's Gym Admin"
admin.site.index_title = "Gym Management System"

# Add custom CSS for admin
class TimmyAdminSite(AdminSite):
    site_header = "Timmy's Elite Performance Center"
    site_title = "Timmy's Gym Admin"
    index_title = "Welcome to Timmy's Gym Management System"