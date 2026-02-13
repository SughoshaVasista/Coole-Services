import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import ServiceCategory, ServiceProvider, Job

def create_test_service():
    cat, _ = ServiceCategory.objects.get_or_create(name='Quick Testing')
    
    user, created = User.objects.get_or_create(
        username='test_5rs',
        defaults={'first_name': 'Aaryan', 'last_name': 'Khan'}
    )
    if created:
        user.set_password('pass123')
        user.save()
        
    prov, _ = ServiceProvider.objects.get_or_create(
        user=user,
        defaults={
            'category': cat,
            'service_code': 'TEST-5',
            'price_per_hour': Decimal('5.00'),
            'status': 'available',
            'description': 'Testing service at 5 INR'
        }
    )
    prov.price_per_hour = Decimal('5.00')
    prov.status = 'available'
    prov.save()
    
    Job.objects.get_or_create(
        provider=prov,
        category=cat,
        defaults={
            'title': '5 Rupee Test Service',
            'base_price': Decimal('5.00'),
            'description': 'Simple test service for payment verification.'
        }
    )
    
    print("SUCCESS: 5 Rupee Test Service and Provider created!")
    print("Username: test_5rs")
    print("Password: pass123")
    print("Price: ₹5.00")

if __name__ == "__main__":
    create_test_service()
