import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import ServiceCategory, ServiceProvider, Job

def create_test_1rs():
    # Using a different category name so it gets a "random/unique" QR 
    # based on the template logic I wrote previously
    cat, _ = ServiceCategory.objects.get_or_create(name='Live Testing')
    
    user, created = User.objects.get_or_create(
        username='test_1rs',
        defaults={'first_name': 'Ishaan', 'last_name': 'Patel'}
    )
    if created:
        user.set_password('pass123')
        user.save()
        
    prov, _ = ServiceProvider.objects.get_or_create(
        user=user,
        defaults={
            'category': cat,
            'service_code': 'TEST-1',
            'price_per_hour': Decimal('1.00'),
            'status': 'available',
            'description': 'Live testing service at 1 INR'
        }
    )
    prov.price_per_hour = Decimal('1.00')
    prov.status = 'available'
    prov.save()
    
    Job.objects.get_or_create(
        provider=prov,
        category=cat,
        defaults={
            'title': '1 Rupee Live Test',
            'base_price': Decimal('1.00'),
            'description': 'Real-world test service for ₹1.'
        }
    )
    
    print("SUCCESS: 1 Rupee Live Test Service created!")
    print("Username: test_1rs")
    print("Password: pass123")
    print("Price: ₹1.00")
    print("Category: Live Testing (Will have unique QR)")

if __name__ == "__main__":
    create_test_1rs()
