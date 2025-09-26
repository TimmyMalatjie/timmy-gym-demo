from django.core.management.base import BaseCommand
from memberships.models import MembershipPlan
from django.contrib.auth.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample data for Timmy\'s Elite Performance Center'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample membership plans...')
        
        # First, let's check what fields actually exist in your model
        # by creating simple plans with only basic fields
        
        # Basic Warrior Plan
        basic, created = MembershipPlan.objects.get_or_create(
            name="Basic Warrior",
            defaults={
                'monthly_price': Decimal('299.00'),
                'description': 'Perfect for getting started with your fitness journey. Access to group classes and basic gym facilities.',
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created: {basic.name}')
        else:
            self.stdout.write(f'  → Exists: {basic.name}')
        
        # Elite Fighter Plan
        elite, created = MembershipPlan.objects.get_or_create(
            name="Elite Fighter", 
            defaults={
                'monthly_price': Decimal('599.00'),
                'description': 'Advanced training with personal coaching. Includes MMA classes and priority booking.',
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created: {elite.name}')
        else:
            self.stdout.write(f'  → Exists: {elite.name}')
        
        # Champion Access Plan
        champion, created = MembershipPlan.objects.get_or_create(
            name="Champion Access",
            defaults={
                'monthly_price': Decimal('999.00'), 
                'description': 'Unlimited access to everything. VIP treatment with dedicated trainer support.',
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created: {champion.name}')
        else:
            self.stdout.write(f'  → Exists: {champion.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample membership plans!')
        )