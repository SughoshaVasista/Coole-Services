import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import ServiceCategory, ServiceProvider, Job, Booking
from profiles.models import UserProfile

def populate_real_time_data():
    print("Setting all providers to 'available'...")
    ServiceProvider.objects.all().update(status='available')

    # 1. Create Sample Customers
    print("Creating sample customers...")
    customers = []
    for i in range(5):
        username = f"customer_{i+1}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f"{username}@gmail.com", 'first_name': f"Customer", 'last_name': str(i+1)}
        )
        if created:
            user.set_password('pass123')
            user.save()
        customers.append(user)
    
    # 2. Ensure every provider has a Job listed
    print("Ensuring every provider has a Job...")
    providers = ServiceProvider.objects.all()
    for p in providers:
        Job.objects.get_or_create(
            provider=p,
            defaults={
                'title': f"{p.category.name} by {p.user.first_name}",
                'category': p.category,
                'description': f"Professional {p.category.name} services offered by {p.user.first_name}.",
                'base_price': p.price_per_hour
            }
        )

    # 3. Create sample bookings (Real-time data)
    print("Creating sample bookings...")
    statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    for _ in range(20):
        customer = random.choice(customers)
        provider = random.choice(providers)
        job = Job.objects.filter(provider=provider).first()
        
        # Random booking date
        booking_date = timezone.now() + timedelta(days=random.randint(-7, 7), hours=random.randint(1, 23))
        
        Booking.objects.get_or_create(
            user=customer,
            provider=provider,
            booking_date=booking_date,
            defaults={
                'service_job': job,
                'status': random.choice(statuses),
                'final_price': provider.price_per_hour,
                'service_location': f"{random.randint(1,999)} Metro St, City Center",
                'notes': random.choice(["Handle with care", "Call before arriving", "Urgent", "None"])
            }
        )
    
    # 4. Ensure all users have profiles
    print("Checking profiles...")
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

    print("SUCCESS: Real-time sample data populated!")

if __name__ == "__main__":
    populate_real_time_data()
