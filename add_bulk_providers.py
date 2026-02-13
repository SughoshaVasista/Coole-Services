import os
import django
import random
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import ServiceCategory, ServiceProvider, Job
from django.contrib.auth.hashers import make_password

def add_bulk_providers():
    print("Adding 50 more providers...")
    categories = list(ServiceCategory.objects.all())
    
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth", 
                   "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", 
                   "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    for i in range(50):
        category = random.choice(categories)
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        service_code = f"BULK-{1000 + i}"
        username = service_code.lower()
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': f_name,
                'last_name': l_name,
                'email': f"{username}@coole.pro",
                'password': make_password('pass123')
            }
        )
        
        if created:
            provider, p_created = ServiceProvider.objects.get_or_create(
                user=user,
                defaults={
                    'category': category,
                    'age': random.randint(22, 55),
                    'rating': round(random.uniform(4.0, 5.0), 1),
                    'price_per_hour': random.randint(20, 100),
                    'contact_number': f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    'address': f"{random.randint(10, 999)} Marketplace Blvd",
                    'service_code': service_code,
                    'description': f"Experienced professional in {category.name}. Certified and ready to help!",
                    'status': 'available'
                }
            )
            
            if p_created:
                Job.objects.create(
                    provider=provider,
                    title=f"{category.name} Expert Service",
                    category=category,
                    description=f"Quick and reliable {category.name} services by {f_name}.",
                    base_price=provider.price_per_hour
                )

    print("SUCCESS: 50 additional providers added and assigned to categories.")

if __name__ == "__main__":
    add_bulk_providers()
