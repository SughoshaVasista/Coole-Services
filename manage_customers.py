import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

from django.contrib.auth.models import User
from profiles.models import UserProfile

def manage_customers():
    # 1. Delete sample customers
    sample_usernames = ['customer_1', 'customer_2', 'customer_3', 'customer_4', 'customer_5']
    deleted = User.objects.filter(username__in=sample_usernames).delete()
    print(f"Removed sample users: {deleted}")

    # 2. Add sughosha as a customer (superuser)
    user, created = User.objects.get_or_create(
        username='sughosha', 
        defaults={
            'is_staff': True, 
            'is_superuser': True, 
            'email': 'sughosha@example.com',
            'first_name': 'Sughosha'
        }
    )
    if created:
        user.set_password('sughosha_12')
        user.save()
        print("Created user 'sughosha' with your password.")
    else:
        print("User 'sughosha' already exists.")

    # 3. Ensure profiles exist for everyone
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

if __name__ == "__main__":
    manage_customers()
