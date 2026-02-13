import os
import django
import random
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import ServiceCategory, ServiceProvider
from profiles.models import UserProfile

def populate():
    print("Starting population script...")

    # 1. Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Superuser 'admin' created with password 'admin'.")
    else:
        print("Superuser 'admin' already exists.")

    # 2. Create Categories
    categories = [
        {'name': 'Home Cleaning', 'desc': 'Professional home cleaning services'},
        {'name': 'Plumbing', 'desc': 'Expert plumbing repairs and installation'},
        {'name': 'Electrical', 'desc': 'Certified electricians for all your needs'},
        {'name': 'Home Salon', 'desc': 'Beauty and grooming services at home'},
        {'name': 'Painting', 'desc': 'Interior and exterior painting services'},
        {'name': 'AC Repair', 'desc': 'AC installation, repair, and maintenance'},
    ]

    for cat_data in categories:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['desc']}
        )
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Category {category.name} already exists.")

    # 3. Create Service Providers
    # We need some dummy users to be providers
    provider_names = [
        ('John', 'Doe', 'Plumbing'),
        ('Jane', 'Smith', 'Home Cleaning'),
        ('Mike', 'Johnson', 'Electrical'),
        ('Sarah', 'Williams', 'Home Salon'),
        ('David', 'Brown', 'Painting'),
        ('Emily', 'Davis', 'AC Repair'),
    ]

    for first, last, cat_name in provider_names:
        username = f"{first.lower()}.{last.lower()}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=f"{username}@example.com", password='password123')
            user.first_name = first
            user.last_name = last
            user.save()
            
            # Get category
            try:
                category = ServiceCategory.objects.get(name=cat_name)
            except ServiceCategory.DoesNotExist:
                print(f"Category {cat_name} not found, skipping provider {username}")
                continue

            # Create ServiceProvider profile
            ServiceProvider.objects.create(
                user=user,
                category=category,
                service_code=f"{cat_name[:3].upper()}-{random.randint(100, 999)}",
                description=f"Experienced {cat_name} professional at Cool-E.",
                age=random.randint(25, 50),
                contact_number=f"555-01{random.randint(10, 99)}",
                address=f"{random.randint(100, 999)} Main St",
                price_per_hour=random.randint(20, 100),
                rating=round(random.uniform(3.5, 5.0), 1),
                status='available' # Ensure they are bookable immediately
            )
            print(f"Created provider: {first} {last} ({cat_name})")
        else:
            print(f"Provider user {username} already exists.")

    print("Population complete!")

if __name__ == '__main__':
    populate()
