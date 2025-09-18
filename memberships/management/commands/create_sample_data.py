from django.core.management.base import BaseCommand
from memberships.models import MembershipPlan
from bookings.models import Service
from accounts.models import TrainerProfile
from django.contrib.auth.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample data for Timmy\'s Elite Performance Center'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for Timmy\'s Gym...')
        
        # Create Membership Plans
        self.create_membership_plans()
        
        # Create Services
        self.create_services()
        
        # Create Sample Trainer (if needed)
        self.create_sample_trainer()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created all sample data!')
        )

    def create_membership_plans(self):
        """Create the three membership tiers"""
        
        # Basic Warrior - Entry level
        basic, created = MembershipPlan.objects.get_or_create(
            name="Basic Warrior",
            defaults={
                'monthly_price': Decimal('299.00'),
                'description': 'Perfect for getting started with your fitness journey. Access to group classes and basic gym facilities.',
                'features': 'Group Classes|Basic Gym Access|Locker Room|Fitness Assessment',
                'classes_included': 8,
                'pt_sessions_included': 0,
                'access_level': 'basic',
                'is_active': True,
                'is_popular': False,
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created: {basic.name}')
        else:
            self.stdout.write(f'  → Exists: {basic.name}')
        
        # Elite Fighter - Most Popular
        elite, created = MembershipPlan.objects.get_or_create(
            name="Elite Fighter",
            defaults={
                'monthly_price': Decimal('599.00'),
                'description': 'Advanced training with personal coaching. Includes MMA classes and priority booking.',
                'features': 'All Group Classes|MMA Training|Personal Training Sessions|Priority Booking|Nutrition Guidance',
                'classes_included': 20,
                'pt_sessions_included': 4,
                'access_level': 'premium',
                'is_active': True,
                'is_popular': True,  # Mark as most popular
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created: {elite.name} (POPULAR)')
        else:
            # Update existing to be popular
            elite.is_popular = True
            elite.save()
            self.stdout.write(f'  → Updated: {elite.name} (POPULAR)')
        
        # Champion Access - Premium tier
        champion, created = MembershipPlan.objects.get_or_create(
            name="Champion Access",
            defaults={
                'monthly_price': Decimal('999.00'),
                'description': 'Unlimited access to everything. VIP treatment with dedicated trainer support.',
                'features': 'Unlimited Everything|Dedicated Trainer|24/7 Access|Corporate Wellness|Guest Passes|Recovery Suite',
                'classes_included': 999,  # Unlimited
                'pt_sessions_included': 12,
                'access_level': 'vip',
                'is_active': True,
                'is_popular': False,
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created: {champion.name}')
        else:
            self.stdout.write(f'  → Exists: {champion.name}')

    def create_services(self):
        """Create the available services for booking"""
        
        services_data = [
            {
                'name': 'Personal Training Session',
                'service_type': 'personal_training',
                'duration_minutes': 60,
                'price': Decimal('150.00'),
                'description': 'One-on-one training session with certified personal trainer',
                'max_capacity': 1,
                'requires_trainer': True,
            },
            {
                'name': 'MMA Training Class',
                'service_type': 'group_class',
                'duration_minutes': 90,
                'price': Decimal('80.00'),
                'description': 'Mixed Martial Arts training class for all skill levels',
                'max_capacity': 12,
                'requires_trainer': True,
            },
            {
                'name': 'HIIT Group Class',
                'service_type': 'group_class',
                'duration_minutes': 45,
                'price': Decimal('50.00'),
                'description': 'High-Intensity Interval Training for maximum results',
                'max_capacity': 15,
                'requires_trainer': True,
            },
            {
                'name': 'Fitness Assessment',
                'service_type': 'assessment',
                'duration_minutes': 30,
                'price': Decimal('75.00'),
                'description': 'Comprehensive fitness evaluation and goal setting',
                'max_capacity': 1,
                'requires_trainer': True,
            },
            {
                'name': 'Boxing Fundamentals',
                'service_type': 'group_class',
                'duration_minutes': 60,
                'price': Decimal('65.00'),
                'description': 'Learn proper boxing technique and conditioning',
                'max_capacity': 10,
                'requires_trainer': True,
            },
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'  ✓ Created service: {service.name}')
            else:
                self.stdout.write(f'  → Exists service: {service.name}')

    def create_sample_trainer(self):
        """Create a sample trainer for demo purposes"""
        
        # Create trainer user if it doesn't exist
        trainer_user, created = User.objects.get_or_create(
            username='trainer_demo',
            defaults={
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'email': 'trainer@timmysgym.com',
                'is_staff': False,
                'is_active': True,
            }
        )
        
        if created:
            trainer_user.set_password('demo123')  # Demo password
            trainer_user.save()
            self.stdout.write(f'  ✓ Created trainer user: {trainer_user.username}')
        
        # Create trainer profile
        trainer_profile, created = TrainerProfile.objects.get_or_create(
            user=trainer_user,
            defaults={
                'specializations': 'MMA|Personal Training|Boxing|HIIT',
                'certifications': 'ACSM Certified|UFC Gym Certified|First Aid CPR',
                'hourly_rate': Decimal('85.00'),
                'bio': 'Certified trainer with 8+ years experience in MMA and personal training. Specializes in functional fitness and combat sports.',
                'years_experience': 8,
                'is_available': True,
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Created trainer profile: {trainer_profile.user.get_full_name()}')
        else:
            self.stdout.write(f'  → Exists trainer profile: {trainer_profile.user.get_full_name()}')