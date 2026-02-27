from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class ServiceProvider(models.Model):
    PROVIDER_STATUS = (
        ('available', 'Available'),
        ('busy', 'Busy / On Job'),
        ('offline', 'Offline'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='providers')
    description = models.TextField()
    contact_number = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    service_code = models.CharField(max_length=20, unique=True, help_text="Unique Service Code e.g. PRO-1234")
    profile_pic = models.ImageField(upload_to='provider_pics/', blank=True, null=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    age = models.IntegerField(default=30, help_text="Provider's age")
    
    # Status for Mutual Exclusion (Uber-like availability)
    status = models.CharField(max_length=20, choices=PROVIDER_STATUS, default='offline')
    
    # Location details
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    current_location = models.CharField(max_length=255, blank=True, help_text="Human readable location")

    def __str__(self):
        category_name = self.category.name if self.category else "No Category"
        status_display = self.get_status_display()
        return f"{self.user.username} - {category_name} ({status_display})"

    @property
    def is_trending(self):
        """Returns True if the provider had > 3 bookings in the last 7 days."""
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_bookings = self.bookings.filter(booking_date__gte=seven_days_ago).count()
        return recent_bookings >= 3

class Job(models.Model):
    """Represents a service listed by a provider or requested by a user"""
    title = models.CharField(max_length=200)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    description = models.TextField()
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, null=True, blank=True, related_name='jobs')
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Requested (Waiting for Partner)'),
        ('accepted', 'Accepted (Waiting for OTP)'),
        ('confirmed', 'In Progress (Work Started)'),
        ('service_done', 'Service Done (Awaiting Payment)'),
        ('paid', 'Paid (Awaiting Verification)'),
        ('completed', 'Finished & Paid'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='bookings')
    service_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True) # Optional linking to specific job
    booking_date = models.DateTimeField() # Slot
    service_location = models.CharField(max_length=255, blank=True, help_text="Where the service should be provided")
    notes = models.TextField(blank=True, help_text="Additional details from the user")
    selected_services = models.TextField(blank=True, null=True, help_text="List of services selected by the user")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_otp = models.CharField(max_length=6, blank=True, null=True)
    
    # Pricing Details
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_kept = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    provider_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tips = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # User feedback
    review_stars = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.provider.user.username} by {self.user.username} on {self.booking_date}"

class Transaction(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI / Online'),
        ('razorpay', 'Razorpay'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    payout = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Razorpay specific fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TXN-{self.id} for Booking {self.booking.id}"

