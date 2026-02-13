from django.contrib import admin
from .models import ServiceCategory, ServiceProvider, Job, Booking, Transaction

# ... existing code ...

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking', 'amount', 'payment_method', 'timestamp')
    list_filter = ('payment_method', 'timestamp')
    search_fields = ('transaction_id', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('timestamp',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'service_code', 'rating', 'price_per_hour')
    list_filter = ('category', 'rating')
    search_fields = ('user__username', 'user__email', 'service_code', 'description')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'provider', 'base_price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'booking_date', 'status', 'created_at')
    list_filter = ('status', 'booking_date', 'created_at')
    search_fields = ('user__username', 'provider__user__username')
