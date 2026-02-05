from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from django.db import OperationalError, ProgrammingError
from django.http import JsonResponse

from .models import MembershipPlan, Membership
from .forms import MembershipPurchaseForm, BillingInfoForm

def membership_plans(request):
    """
    Public membership plans display - like character class selection
    Available to all visitors
    """
    plans_list = []
    try:
        plans = MembershipPlan.objects.filter(is_active=True).order_by('sort_order', 'monthly_price')
        # Convert QuerySet to list and add popular plan indicator
        plans_list = list(plans)
        if len(plans_list) >= 3:
            plans_list[1].is_popular = True
    except (OperationalError, ProgrammingError):
        plans_list = []
    
    context = {
        'plans': plans_list,  # Use the modified list instead of QuerySet
        'user_has_membership': False,
    }
    
    # Check if user has active membership
    if request.user.is_authenticated:
        try:
            membership = Membership.objects.get(user=request.user)
            context['user_has_membership'] = membership.is_active
            context['current_membership'] = membership
        except Membership.DoesNotExist:
            pass
        except (OperationalError, ProgrammingError):
            pass
    
    return render(request, 'memberships/plans.html', context)
@login_required
def membership_purchase(request, plan_id):
    """
    Membership purchase flow - like buying a game upgrade
    Step 1: Plan selection and user info confirmation
    """
    try:
        plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)
    except (OperationalError, ProgrammingError):
        messages.error(request, 'Membership data is temporarily unavailable. Please try again shortly.')
        return redirect('memberships:plans')
    
    # Check if user already has active membership
    try:
        existing_membership = Membership.objects.get(user=request.user)
        if existing_membership.is_active:
            messages.warning(request, 'You already have an active membership. You can upgrade or cancel your current plan.')
            return redirect('memberships:membership_manage')
    except Membership.DoesNotExist:
        pass
    except (OperationalError, ProgrammingError):
        messages.error(request, 'Membership data is temporarily unavailable. Please try again shortly.')
        return redirect('memberships:plans')
    
    if request.method == 'POST':
        form = MembershipPurchaseForm(request.POST, user=request.user, plan=plan)
        if form.is_valid():
            # Store form data in session for payment step
            request.session['membership_purchase'] = {
                'plan_id': plan.id,
                'start_immediately': form.cleaned_data['start_immediately'],
                'billing_cycle': form.cleaned_data['billing_cycle'],
                'agree_terms': form.cleaned_data['agree_terms'],
            }
            return redirect('memberships:membership_checkout')
    else:
        form = MembershipPurchaseForm(user=request.user, plan=plan)
    
    context = {
        'plan': plan,
        'form': form,
        'user': request.user,
    }
    return render(request, 'memberships/purchase.html', context)

@login_required
def membership_checkout(request):
    """
    Payment processing page - like in-game store checkout
    Step 2: Payment information and processing
    """
    # Get purchase data from session
    purchase_data = request.session.get('membership_purchase')
    if not purchase_data:
        messages.error(request, 'Invalid purchase session. Please select a plan again.')
        return redirect('memberships:plans')
    
    try:
        plan = get_object_or_404(MembershipPlan, id=purchase_data['plan_id'])
    except (OperationalError, ProgrammingError):
        messages.error(request, 'Membership data is temporarily unavailable. Please try again shortly.')
        return redirect('memberships:plans')
    
    if request.method == 'POST':
        billing_form = BillingInfoForm(request.POST)
        if billing_form.is_valid():
            # Mock payment processing
            payment_success = process_mock_payment(
                user=request.user,
                plan=plan,
                billing_info=billing_form.cleaned_data,
                purchase_data=purchase_data
            )
            
            if payment_success:
                # Create membership
                create_membership(request.user, plan, purchase_data)
                
                # Clear session data
                del request.session['membership_purchase']
                
                messages.success(request, f'Welcome to {plan.name}! Your membership is now active.')
                return redirect('memberships:membership_success')
            else:
                messages.error(request, 'Payment processing failed. Please try again.')
    else:
        billing_form = BillingInfoForm()
    
    # Calculate total cost
    total_cost = plan.monthly_price + plan.setup_fee
    
    context = {
        'plan': plan,
        'billing_form': billing_form,
        'total_cost': total_cost,
        'monthly_cost': plan.monthly_price,
        'setup_fee': plan.setup_fee,
        'purchase_data': purchase_data,
    }
    return render(request, 'memberships/checkout.html', context)

@login_required
def membership_success(request):
    """
    Purchase confirmation page - quest completed screen
    """
    # Get user's latest membership
    try:
        membership = Membership.objects.get(user=request.user)
    except Membership.DoesNotExist:
        messages.error(request, 'No membership found.')
        return redirect('memberships:plans')
    except (OperationalError, ProgrammingError):
        messages.error(request, 'Membership data is temporarily unavailable. Please try again shortly.')
        return redirect('memberships:plans')
    
    context = {
        'membership': membership,
        'plan': membership.plan,
    }
    return render(request, 'memberships/success.html', context)

@method_decorator(login_required, name='dispatch')
class MembershipManageView(DetailView):
    """
    Membership management dashboard - player account screen
    """
    template_name = 'memberships/manage.html'
    context_object_name = 'membership'
    
    def get_object(self):
        try:
            return Membership.objects.get(user=self.request.user)
        except Membership.DoesNotExist:
            return None
        except (OperationalError, ProgrammingError):
            return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = self.get_object()
        
        if membership:
            # Calculate usage statistics
            context['usage_stats'] = {
                'classes_used': membership.classes_used_this_month,
                'classes_included': membership.plan.group_classes_included,
                'pt_sessions_used': membership.pt_sessions_used_this_month,
                'pt_sessions_included': membership.plan.personal_training_sessions,
            }
            
            # Check if unlimited classes
            if membership.plan.group_classes_included == 0:
                context['usage_stats']['classes_unlimited'] = True
            
            # Calculate days remaining
            if membership.end_date:
                days_remaining = (membership.end_date - timezone.now().date()).days
                context['days_remaining'] = max(0, days_remaining)
            
            # Available upgrade options
            try:
                context['upgrade_options'] = MembershipPlan.objects.filter(
                    is_active=True,
                    monthly_price__gt=membership.plan.monthly_price
                ).order_by('monthly_price')
            except (OperationalError, ProgrammingError):
                context['upgrade_options'] = []
        
        try:
            context['available_plans'] = MembershipPlan.objects.filter(is_active=True)
        except (OperationalError, ProgrammingError):
            context['available_plans'] = []
        return context

@login_required
def membership_cancel(request):
    """
    Membership cancellation - unsubscribe flow
    """
    try:
        membership = Membership.objects.get(user=request.user)
    except Membership.DoesNotExist:
        messages.error(request, 'No active membership found.')
        return redirect('memberships:plans')
    except (OperationalError, ProgrammingError):
        messages.error(request, 'Membership data is temporarily unavailable. Please try again shortly.')
        return redirect('memberships:plans')
    
    if not membership.is_active:
        messages.warning(request, 'Your membership is already inactive.')
        return redirect('memberships:membership_manage')
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('reason', '')
        
        # Set membership to cancelled (keeps access until end date)
        membership.status = 'cancelled'
        membership.save()
        
        # Log cancellation reason (you could create a CancellationLog model)
        
        messages.success(request, 'Your membership has been cancelled. You will retain access until your current billing period ends.')
        return redirect('memberships:membership_manage')
    
    context = {
        'membership': membership,
        'plan': membership.plan,
    }
    return render(request, 'memberships/cancel.html', context)

@login_required
def membership_upgrade(request, plan_id):
    """
    Upgrade existing membership - character class upgrade
    """
    try:
        new_plan = get_object_or_404(MembershipPlan, id=plan_id, is_active=True)
    except (OperationalError, ProgrammingError):
        messages.error(request, 'Membership data is temporarily unavailable. Please try again shortly.')
        return redirect('memberships:plans')
    
    try:
        current_membership = Membership.objects.get(user=request.user)
    except Membership.DoesNotExist:
        messages.error(request, 'No current membership found.')
        return redirect('memberships:plans')
    except (OperationalError, ProgrammingError):
        messages.error(request, 'Membership data is temporarily unavailable. Please try again shortly.')
        return redirect('memberships:plans')
    
    # Check if this is actually an upgrade
    if new_plan.monthly_price <= current_membership.plan.monthly_price:
        messages.error(request, 'You can only upgrade to a higher-tier plan.')
        return redirect('memberships:membership_manage')
    
    if request.method == 'POST':
        # Calculate prorated costs
        days_remaining = (current_membership.end_date - timezone.now().date()).days
        current_daily_rate = current_membership.plan.monthly_price / 30
        new_daily_rate = new_plan.monthly_price / 30
        
        prorated_cost = (new_daily_rate - current_daily_rate) * days_remaining
        
        # Mock payment processing for upgrade
        if process_mock_payment(request.user, new_plan, {}, {'upgrade': True}):
            # Update membership
            current_membership.plan = new_plan
            current_membership.save()
            
            messages.success(request, f'Successfully upgraded to {new_plan.name}!')
            return redirect('memberships:membership_manage')
        else:
            messages.error(request, 'Upgrade payment failed. Please try again.')
    
    # Calculate upgrade costs
    days_remaining = (current_membership.end_date - timezone.now().date()).days
    current_daily_rate = current_membership.plan.monthly_price / 30
    new_daily_rate = new_plan.monthly_price / 30
    prorated_cost = (new_daily_rate - current_daily_rate) * max(1, days_remaining)
    
    context = {
        'current_membership': current_membership,
        'new_plan': new_plan,
        'prorated_cost': prorated_cost,
        'days_remaining': days_remaining,
    }
    return render(request, 'memberships/upgrade.html', context)

@login_required
def membership_billing_history(request):
    """
    Billing history and invoices - transaction log
    """
    try:
        membership = Membership.objects.get(user=request.user)
    except Membership.DoesNotExist:
        messages.error(request, 'No membership found.')
        return redirect('memberships:plans')
    
    # Mock billing history (you would integrate with actual payment provider)
    mock_transactions = generate_mock_billing_history(membership)
    
    context = {
        'membership': membership,
        'transactions': mock_transactions,
    }
    return render(request, 'memberships/billing_history.html', context)

def membership_compare(request):
    """
    Plan comparison tool - feature matrix
    """
    plans = MembershipPlan.objects.filter(is_active=True).order_by('sort_order', 'monthly_price')
    
    # Create feature comparison matrix
    features = [
        {'name': 'Gym Access', 'key': 'gym_access'},
        {'name': 'Group Classes', 'key': 'group_classes_included'},
        {'name': 'Personal Training', 'key': 'personal_training_sessions'},
        {'name': 'Guest Passes', 'key': 'guest_passes'},
    ]
    
    context = {
        'plans': plans,
        'features': features,
    }
    return render(request, 'memberships/compare.html', context)

# Helper Functions

def process_mock_payment(user, plan, billing_info, purchase_data):
    """
    Mock payment processing - simulates successful payment
    In production, integrate with Stripe, PayFast, or other payment provider
    """
    # Simulate payment processing delay
    import time
    time.sleep(1)
    
    # Mock validation
    if billing_info.get('card_number', '').startswith('4111'):
        return True  # Success
    elif billing_info.get('card_number', '').startswith('4000'):
        return False  # Decline
    else:
        return True  # Default success for demo

def create_membership(user, plan, purchase_data):
    """
    Create new membership record
    """
    start_date = timezone.now().date()
    if not purchase_data.get('start_immediately', True):
        # Could allow future start dates
        pass
    
    end_date = start_date + timedelta(days=30)  # Monthly billing
    next_billing = end_date
    
    # Delete any existing membership
    Membership.objects.filter(user=user).delete()
    
    # Create new membership
    membership = Membership.objects.create(
        user=user,
        plan=plan,
        status='active',
        start_date=start_date,
        end_date=end_date,
        next_billing_date=next_billing,
    )
    
    return membership

def generate_mock_billing_history(membership):
    """
    Generate mock billing transactions for demo
    """
    transactions = []
    current_date = membership.start_date
    
    while current_date <= timezone.now().date():
        transactions.append({
            'date': current_date,
            'description': f'{membership.plan.name} - Monthly Subscription',
            'amount': membership.plan.monthly_price,
            'status': 'Paid',
            'invoice_number': f'INV-{current_date.strftime("%Y%m%d")}-{membership.id}',
        })
        current_date += timedelta(days=30)
    
    return transactions[:6]  # Last 6 transactions

@login_required
def check_membership_status(request):
    """
    AJAX endpoint for checking membership status
    Used for dashboard updates
    """
    try:
        membership = Membership.objects.get(user=request.user)
        data = {
            'has_membership': True,
            'is_active': membership.is_active,
            'plan_name': membership.plan.name,
            'end_date': membership.end_date.isoformat(),
            'days_remaining': (membership.end_date - timezone.now().date()).days,
            'classes_used': membership.classes_used_this_month,
            'classes_included': membership.plan.group_classes_included,
        }
    except Membership.DoesNotExist:
        data = {
            'has_membership': False,
            'is_active': False,
        }
    
    return JsonResponse(data)