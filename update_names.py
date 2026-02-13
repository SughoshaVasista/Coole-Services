import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from django.contrib.auth.models import User
from services.models import ServiceProvider, Job

def update_to_indian_names():
    indian_first_names = [
        "Rajesh", "Suresh", "Amit", "Priya", "Ananya", "Vikram", "Arjun", "Sneha", 
        "Rohan", "Pooja", "Sanjay", "Lakshmi", "Kavita", "Rahul", "Deepa", "Sunil", 
        "Anita", "Manish", "Rekha", "Vinod", "Neelam", "Ravi", "Shanti", "Ashok", 
        "Meena", "Dinesh", "Sangeeta", "Kishore", "Savita", "Gopal"
    ]
    
    indian_last_names = [
        "Sharma", "Verma", "Gupta", "Singh", "Iyer", "Patel", "Reddy", "Nair", 
        "Chatterjee", "Joshi", "Kulkarni", "Mehta", "Kapoor", "Malhotra", "Agarwal", 
        "Bansal", "Choudhary", "Ghosh", "Jha", "Rao"
    ]

    providers = ServiceProvider.objects.all()
    print(f"Updating {providers.count()} providers to Indian names...")

    for provider in providers:
        user = provider.user
        
        # Special handling for test users to keep them recognizable but Indian
        if user.username == 'test_5rs':
            new_first = "Aaryan"
            new_last = "Khan"
        elif user.username == 'test_1rs':
            new_first = "Ishaan"
            new_last = "Patel"
        else:
            new_first = random.choice(indian_first_names)
            new_last = random.choice(indian_last_names)
        
        old_full_name = f"{user.first_name} {user.last_name}"
        user.first_name = new_first
        user.last_name = new_last
        user.save()
        
        new_full_name = f"{new_first} {new_last}"
        
        # Update provider description if it mentions the old name or is generic
        if "professional" in provider.description.lower():
            provider.description = f"Hi, I am {new_full_name}, an experienced professional in {provider.category.name}. Ready to serve you with quality work!"
        
        # Update contact number to Indian format if it's default
        if "+1" in provider.contact_number or "(555)" in provider.contact_number:
            provider.contact_number = f"+91 {random.randint(7000, 9999)}{random.randint(100000, 999999)}"
            
        provider.save()

        # Update associated Jobs
        jobs = Job.objects.filter(provider=provider)
        for job in jobs:
            if old_full_name in job.description:
                job.description = job.description.replace(old_full_name, new_full_name)
            elif "by" in job.description:
                # Fallback for generic 'by Name'
                job.description = f"{job.title} provided with excellence by {new_full_name}."
            job.save()

    print("SUCCESS: All service providers updated with Indian names and contact details.")

if __name__ == "__main__":
    update_to_indian_names()
