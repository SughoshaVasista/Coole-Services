import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from services.models import ServiceProvider

def update_providers():
    providers = ServiceProvider.objects.all()
    
    addresses = [
        "123 MG Road, Bangalore, Karnataka 560001",
        "456 Park Avenue, Mumbai, Maharashtra 400001",
        "789 Residency Road, Delhi 110001",
        "12 Mall Road, Shimla, Himachal Pradesh 171001",
        "54 Brigade Road, Chennai, Tamil Nadu 600001",
        "88 Lake View, Hyderabad, Telangana 500001",
        "101 Marine Drive, Mumbai, Maharashtra 400020",
        "22 MG Road, Pune, Maharashtra 411001",
        "33 Commercial Street, Bangalore, Karnataka 560042",
        "99 Gachibowli, Hyderabad, Telangana 500032",
        "77 Salt Lake, Kolkata, West Bengal 700091",
        "15 Anna Salai, Chennai, Tamil Nadu 600002",
        "44 Hazratganj, Lucknow, Uttar Pradesh 226001",
        "66 Sector 17, Chandigarh 160017",
        "11 SG Highway, Ahmedabad, Gujarat 380054"
    ]
    
    print(f"Updating {providers.count()} service providers...")
    
    for provider in providers:
        # Generate a random Indian mobile number
        phone = f"{random.choice(['6', '7', '8', '9'])}{''.join([str(random.randint(0, 9)) for _ in range(9)])}"
        
        # Pick a random address
        address = random.choice(addresses)
        
        provider.contact_number = phone
        provider.address = address
        provider.save()
        
        print(f"Updated: {provider.user.username} | Phone: {phone} | Address: {address}")

    print("\nSUCCESS: All service providers updated with contact numbers and addresses!")

if __name__ == "__main__":
    update_providers()
