import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunet_pro.settings')
django.setup()

import razorpay

try:
    print(f"Key ID: {settings.RAZORPAY_KEY_ID}")
    print(f"Key Secret: {settings.RAZORPAY_KEY_SECRET}")
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    print("Razorpay client initialized successfully.")
except Exception as e:
    print(f"Error initializing Razorpay client: {e}")
