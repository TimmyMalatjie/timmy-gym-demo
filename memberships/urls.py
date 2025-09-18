# memberships/urls.py
from django.urls import path
from . import views

app_name = 'memberships'

urlpatterns = [
    # Public pages
    path('plans/', views.membership_plans, name='membership_plans'),
    path('compare/', views.membership_compare, name='membership_compare'),
    
    # Purchase flow
    path('purchase/<int:plan_id>/', views.membership_purchase, name='membership_purchase'),
    path('checkout/', views.membership_checkout, name='membership_checkout'),
    path('success/', views.membership_success, name='membership_success'),
    
    # Management (login required)
    path('manage/', views.MembershipManageView.as_view(), name='membership_manage'),
    path('upgrade/<int:plan_id>/', views.membership_upgrade, name='membership_upgrade'),
    path('cancel/', views.membership_cancel, name='membership_cancel'),
    path('billing-history/', views.membership_billing_history, name='membership_billing_history'),
    
    # AJAX endpoints
    path('api/status/', views.check_membership_status, name='membership_status_api'),
]