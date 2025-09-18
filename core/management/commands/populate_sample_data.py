# core/management/commands/populate_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from memberships.models import MembershipPlan
from bookings.models import Service
from accounts.models import UserProfile, TrainerProfile

class Command(BaseCommand):
    help = 'Populate database with sample data for demo'

    def handle(self, *args, **options):
        self.stdout.write('🎮 Creating sample data for Timmy\'s Gym...')

        # Create Membership Plans
        plans = [
            {
                'name': 'Basic Warrior',
                'plan_type': 'basic',
                'description': 'Perfect for beginners. Gym access and basic facilities.',
                'monthly_price': 299.00,
                'group_classes_included': 4,
                'personal_training_sessions': 0,
                'guest_passes': 1,
            },
            {
                'name': 'Elite Fighter',
                'plan_type': 'premium',
                'description': 'For serious athletes. Includes MMA training and unlimited classes.',
                'monthly_price': 599.00,
                'group_classes_included': 0,  # Unlimited
                'personal_training_sessions': 2,
                'guest_passes': 3,
            },
            {
                'name': 'Champion Access',
                'plan_type': 'vip',
                'description': 'Premium membership with personal training and all perks.',
                'monthly_price': 999.00,
                'group_classes_included': 0,  # Unlimited
                'personal_training_sessions': 8,
                'guest_passes': 5,
            }
        ]

        for plan_data in plans:
            plan, created = MembershipPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'✅ Created plan: {plan.name}')

        # Create Services
        services = [
            {
                'name': 'Personal Training Session',
                'service_type': 'personal_training',
                'description': '1-on-1 training with certified trainer',
                'duration_minutes': 60,
                'price': 150.00,
                'max_participants': 1,
            },
            {
                'name': 'MMA Training',
                'service_type': 'mma_session',
                'description': 'Mixed martial arts training session',
                'duration_minutes': 90,
                'price': 200.00,
                'max_participants': 1,
            },
            {
                'name': 'HIIT Group Class',
                'service_type': 'group_class',
                'description': 'High-intensity interval training',
                'duration_minutes': 45,
                'price': 80.00,
                'max_participants': 15,
            },
            {
                'name': 'Fitness Assessment',
                'service_type': 'assessment',
                'description': 'Complete fitness evaluation and goal setting',
                'duration_minutes': 90,
                'price': 250.00,
                'max_participants': 1,
            }
        ]

        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'✅ Created service: {service.name}')

        self.stdout.write(
            self.style.SUCCESS('🏆 Sample data created successfully!')
        )