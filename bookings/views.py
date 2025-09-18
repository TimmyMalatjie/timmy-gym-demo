# bookings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.db.models import Q

from .models import Service, Booking
from .forms import BookingForm
from accounts.models import TrainerProfile

def services_list(request):
    """
    Public services catalog - quest selection screen
    No login required for browsing.
    """
    services = Service.objects.filter(is_active=True)
    
    # Filter by service type
    service_type = request.GET.get('type')
    if service_type:
        services = services.filter(service_type=service_type)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(services, 9)  # 9 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'service_types': Service.SERVICE_TYPES,
        'current_filters': {
            'type': service_type or '',
            'search': search_query or '',
        }
    }
    return render(request, 'bookings/services_list.html', context)

# ---

@login_required
def booking_calendar(request):
    """
    Interactive calendar view - like a raid planner for gym sessions.
    Shows all available services and time slots.
    """
    services = Service.objects.filter(is_active=True)
    service_filter = request.GET.get('service', '')
    
    if service_filter:
        services = services.filter(id=service_filter)
    
    available_slots = []
    start_date = timezone.now().date()
    
    for i in range(30):  # Next 30 days
        current_date = start_date + timedelta(days=i)
        
        for hour in range(9, 21):  # 9 AM to 8 PM
            slot_time = time(hour, 0)
            
            for service in services:
                existing_bookings = Booking.objects.filter(
                    service=service,
                    date=current_date,
                    start_time=slot_time,
                    status__in=['pending', 'confirmed']
                ).count()
                
                if existing_bookings < service.max_participants:
                    available_slots.append({
                        'date': current_date,
                        'time': slot_time,
                        'service': service,
                        'spots_left': service.max_participants - existing_bookings
                    })
    
    user_bookings = Booking.objects.filter(
        user=request.user,
        date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'start_time')[:5]
    
    context = {
        'services': Service.objects.filter(is_active=True),
        'available_slots': available_slots[:50],
        'user_bookings': user_bookings,
        'selected_service': service_filter,
        'today': start_date,
    }
    return render(request, 'bookings/calendar.html', context)

# ---

@method_decorator(login_required, name='dispatch')
class BookingCreateView(CreateView):
    """
    Create a new booking - like starting a new quest.
    """
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_create.html'
    success_url = reverse_lazy('bookings:booking_success')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        service = form.instance.service
        start_datetime = datetime.combine(form.instance.date, form.instance.start_time)
        end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)
        form.instance.end_time = end_datetime.time()
        form.instance.amount_paid = service.price
        
        # Check for user conflicts
        conflicting_bookings = Booking.objects.filter(
            user=self.request.user,
            date=form.instance.date,
            start_time=form.instance.start_time,
            status__in=['pending', 'confirmed']
        )
        if conflicting_bookings.exists():
            messages.error(self.request, 'You already have a booking at this time!')
            return self.form_invalid(form)
        
        # Check capacity
        existing_bookings = Booking.objects.filter(
            service=service,
            date=form.instance.date,
            start_time=form.instance.start_time,
            status__in=['pending', 'confirmed']
        ).count()
        if existing_bookings >= service.max_participants:
            messages.error(self.request, 'This time slot is fully booked!')
            return self.form_invalid(form)
        
        messages.success(self.request, f'Booking created successfully! Your {service.name} session is scheduled.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.request.GET.get('service_id')
        if service_id:
            try:
                context['selected_service'] = get_object_or_404(Service, id=service_id)
            except Exception:
                pass
        
        context['services'] = Service.objects.filter(is_active=True)
        context['trainers'] = TrainerProfile.objects.filter(is_accepting_clients=True)
        return context

# ---

@login_required
def booking_success(request):
    """
    Booking confirmation page - quest accepted screen.
    """
    latest_booking = Booking.objects.filter(user=request.user).order_by('-created_at').first()
    context = {'booking': latest_booking}
    return render(request, 'bookings/booking_success.html', context)

# ---

@method_decorator(login_required, name='dispatch')
class BookingListView(ListView):
    """
    User's booking history - quest journal.
    """
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Booking.objects.filter(user=self.request.user).order_by('-date', '-start_time')
        
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        service_filter = self.request.GET.get('service')
        if service_filter:
            queryset = queryset.filter(service__id=service_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)
        context['status_choices'] = Booking.STATUS_CHOICES
        context['current_filters'] = {
            'status': self.request.GET.get('status', 'all'),
            'service': self.request.GET.get('service', ''),
        }
        context['today'] = timezone.now().date()
        
        bookings = self.get_queryset()
        context['stats'] = {
            'total_bookings': bookings.count(),
            'completed_sessions': bookings.filter(status='completed').count(),
            'upcoming_sessions': bookings.filter(
                date__gte=timezone.now().date(),
                status__in=['pending', 'confirmed']
            ).count(),
            'cancelled_sessions': bookings.filter(status='cancelled').count(),
        }
        return context

# ---

@login_required
def booking_detail(request, booking_id):
    """
    Individual booking management - quest details screen.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    booking_datetime = datetime.combine(booking.date, booking.start_time)
    booking_datetime = timezone.make_aware(booking_datetime)
    can_cancel_or_reschedule = booking_datetime > timezone.now() + timedelta(hours=24)
    
    context = {
        'booking': booking,
        'can_cancel': can_cancel_or_reschedule,
        'can_reschedule': can_cancel_or_reschedule and booking.status in ['pending', 'confirmed'],
    }
    return render(request, 'bookings/booking_detail.html', context)

# ---

@login_required
def booking_cancel(request, booking_id):
    """
    Cancel a booking - abandon quest.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    booking_datetime = timezone.make_aware(datetime.combine(booking.date, booking.start_time))
    if booking_datetime <= timezone.now() + timedelta(hours=24):
        messages.error(request, 'Cannot cancel bookings less than 24 hours in advance.')
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, f'Your {booking.service.name} session has been cancelled.')
        return redirect('bookings:booking_list')
    
    context = {'booking': booking}
    return render(request, 'bookings/booking_cancel.html', context)

# ---

@login_required
def booking_reschedule(request, booking_id):
    """
    Reschedule an existing booking - change quest time.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    booking_datetime = timezone.make_aware(datetime.combine(booking.date, booking.start_time))
    if booking_datetime <= timezone.now() + timedelta(hours=24):
        messages.error(request, 'Cannot reschedule bookings less than 24 hours in advance.')
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be rescheduled.')
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, user=request.user)
        if form.is_valid():
            service = form.instance.service
            start_datetime = datetime.combine(form.instance.date, form.instance.start_time)
            end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)
            form.instance.end_time = end_datetime.time()
            
            form.save()
            messages.success(request, 'Your booking has been rescheduled successfully!')
            return redirect('bookings:booking_detail', booking_id=booking_id)
    else:
        form = BookingForm(instance=booking, user=request.user)
    
    context = {
        'form': form,
        'booking': booking,
        'services': Service.objects.filter(is_active=True),
        'trainers': TrainerProfile.objects.filter(is_accepting_clients=True),
    }
    return render(request, 'bookings/booking_reschedule.html', context)

# ---

@login_required
def get_available_times(request):
    """
    AJAX endpoint to get available times for a specific date and service.
    """
    service_id = request.GET.get('service_id')
    date_str = request.GET.get('date')
    
    if not service_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        service = Service.objects.get(id=service_id, is_active=True)
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (Service.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    
    if booking_date < timezone.now().date():
        return JsonResponse({'times': []})
    
    available_times = []
    for hour in range(9, 21):
        slot_time = time(hour, 0)
        existing_bookings = Booking.objects.filter(
            service=service,
            date=booking_date,
            start_time=slot_time,
            status__in=['pending', 'confirmed']
        ).count()
        
        if existing_bookings < service.max_participants:
            available_times.append({
                'time': slot_time.strftime('%H:%M'),
                'display': slot_time.strftime('%I:%M %p'),
                'spots_left': service.max_participants - existing_bookings
            })
    
    return JsonResponse({'times': available_times})