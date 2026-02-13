from django.shortcuts import render, get_object_or_404, redirect
from .models import ServiceCategory, ServiceProvider, Booking
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import uuid
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction

def services_view(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category') 
    
    categories = ServiceCategory.objects.all()

    if query:
        # Search for categories or providers matching the query
        categories = categories.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(providers__user__first_name__icontains=query) |
            Q(providers__user__last_name__icontains=query) |
            Q(providers__description__icontains=query)
        ).distinct()

    if category_slug:
        # Filter by specific category slug/name if clicked from landing page
        # Using name__icontains for now as simple slug match
        categories = categories.filter(name__icontains=category_slug)

    return render(request, 'services.html', {'categories': categories})

def category_detail_view(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    # Strict Mutual Exclusion: Only show providers who are currently 'available'
    providers = ServiceProvider.objects.filter(category=category, status='available')
    return render(request, 'category_detail.html', {'category': category, 'providers': providers})

def provider_detail_view(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    return render(request, 'provider_detail.html', {'provider': provider})

@login_required
def book_provider_view(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    if request.method == 'POST':
        date_str = request.POST.get('date')
        
        if not date_str:
            messages.error(request, "Please select a valid date and time.")
            return redirect('provider_detail', provider_id=provider.id)

        try:
            booking_date = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%dT%H:%M'))
        except ValueError:
             # Fallback formats just in case
            try:
                booking_date = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%d %H:%M'))
            except ValueError:
                 messages.error(request, "Invalid date format.")
                 return redirect('provider_detail', provider_id=provider.id)

        # Basic Check: Don't book in the past
        if booking_date < timezone.now():
             messages.error(request, "Cannot book appointments in the past.")
             return redirect('provider_detail', provider_id=provider.id)

        # Strict Mutual Exclusion Check
        if provider.status != 'available':
             messages.error(request, "This provider is currently busy or offline. Please choose another.")
             return redirect('category_detail', category_id=provider.category.id)

        # Create Booking with location and notes
        booking = Booking.objects.create(
            user=request.user,
            provider=provider,
            booking_date=booking_date,
            service_location=request.POST.get('service_location', ''),
            notes=request.POST.get('notes', ''),
            status='pending', 
        )
        
        # NOTE: Booking is pending. Provider remains available until payment is confirmed.
        # This prevents blocking providers by users who might not complete payment.

        messages.success(request, "Booking request initiated! Please complete the payment to confirm your schedule.")
        return redirect('pay_via_upi', booking_id=booking.id) 

    return redirect('provider_detail', provider_id=provider.id)

@login_required
def partner_dashboard_view(request):
    try:
        provider = request.user.service_provider
    except (AttributeError, ServiceProvider.DoesNotExist):
        messages.error(request, "You are not registered as a partner.")
        return redirect('home')

    # Status Toggle Logic
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_status':
            new_status = request.POST.get('status')
            # Only allow manual toggle if not currently in a booked job (Busy)
            # Unless completing a job which sets to available.
            # Here we are just toggling availability.
            if new_status in ['available', 'offline']:
                provider.status = new_status
                provider.save()
                messages.success(request, f"Status updated to {new_status}")
            else:
                messages.error(request, "You cannot manually set status to 'Busy'. Accept a job to become Busy.")
        
        elif action == 'manage_job':
            booking_id = request.POST.get('booking_id')
            job_action = request.POST.get('job_action') # accept, complete, reject
            booking = get_object_or_404(Booking, id=booking_id, provider=provider)
            
            if job_action == 'accept':
                booking.status = 'confirmed'
                booking.save()
                # Ensure provider becomes busy
                provider.status = 'busy' 
                provider.save()
                messages.success(request, "Job Accepted! You are now Busy.")
            
            elif job_action == 'complete':
                # Business Logic: Calculate Commission (20%)
                from decimal import Decimal
                COMMISSION_RATE = Decimal('0.20')
                
                final_price = booking.final_price if booking.final_price else provider.price_per_hour
                commission = (final_price * COMMISSION_RATE).quantize(Decimal('0.01'))
                payout = final_price - commission
                
                booking.status = 'completed'
                booking.final_price = final_price
                booking.commission_kept = commission
                booking.provider_payout = payout
                booking.save()
                
                # Store Transaction Detail
                from .models import Transaction
                import uuid
                payment_method = request.POST.get('payment_method', 'cash')
                
                transaction, created = Transaction.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'amount': final_price,
                        'commission': commission,
                        'payout': payout,
                        'payment_method': payment_method,
                        'transaction_id': f"TXN-{uuid.uuid4().hex[:10].upper()}"
                    }
                )
                if not created and transaction.payment_method == 'razorpay':
                    # Update commission and payout if it was just an order initiation before
                    transaction.commission = commission
                    transaction.payout = payout
                    transaction.save()

                # Free up the provider
                provider.status = 'available'
                provider.save()
                messages.success(request, f"Job Completed! ₹{payout} credited to your account. Cool-E commission: ₹{commission}")
            
            elif job_action == 'reject':

                booking.status = 'cancelled'
                booking.save()
                # Free up the provider
                provider.status = 'available'
                provider.save()
                messages.warning(request, "Job Rejected. You are now available for other bookings.")

        return redirect('partner_dashboard')

    # Fetch active/pending jobs
    # Pending: Needs acceptance
    # Confirmed: Currently working on it
    incoming_requests = Booking.objects.filter(provider=provider, status='pending').order_by('booking_date')
    active_jobs = Booking.objects.filter(provider=provider, status='confirmed').order_by('booking_date')
    completed_jobs = Booking.objects.filter(provider=provider, status='completed').select_related('transaction').order_by('-booking_date')[:5]

    return render(request, 'partner_dashboard.html', {
        'provider': provider,
        'incoming_requests': incoming_requests,
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs
    })

# API Views for Postman
from django.http import JsonResponse

def get_services_json(request):
    categories = ServiceCategory.objects.all()
    data = []
    for cat in categories:
        data.append({
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'provider_count': cat.providers.count()
        })
    return JsonResponse({'status': 'success', 'data': data}, safe=False)

def get_providers_json(request):
    providers = ServiceProvider.objects.all()
    data = []
    for p in providers:
        data.append({
            'id': p.id,
            'username': p.user.username,
            'category': p.category.name if p.category else None,
            'status': p.status,
            'rating': p.rating,
            'price_per_hour': float(p.price_per_hour),
            'contact_number': p.contact_number,
            'service_code': p.service_code
        })
    return JsonResponse({'status': 'success', 'data': data}, safe=False)

# Razorpay Implementation
import razorpay
from decimal import Decimal

@login_required
def initiate_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Calculate amount in paise (1 INR = 100 paise)
    amount = int(booking.provider.price_per_hour * 100)
    
    # Create Razorpay Order
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1' # Auto capture
    }
    
    try:
        razorpay_order = client.order.create(data=order_data)
        
        # Calculate commission and payout using Decimal
        from decimal import Decimal
        total_price = booking.provider.price_per_hour
        commission = (total_price * Decimal('0.20')).quantize(Decimal('0.01'))
        payout = total_price - commission
        
        # Update or Create Transaction
        transaction, created = Transaction.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': total_price,
                'commission': commission,
                'payout': payout,
                'payment_method': 'razorpay',
                'razorpay_order_id': razorpay_order['id']
            }
        )
        
        if not created:
            transaction.razorpay_order_id = razorpay_order['id']
            transaction.payment_method = 'razorpay'
            transaction.commission = commission
            transaction.payout = payout
            transaction.save()


        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'callback_url': request.build_absolute_uri('/services/payment-callback/'),
            'booking': booking
        }
        
        return render(request, 'payment_checkout.html', context)
    except Exception as e:
        messages.error(request, f"Error creating payment order: {str(e)}")
        return redirect('orders')

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        # Initialize Razorpay Client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)
            
            # Update Transaction
            transaction = Transaction.objects.get(razorpay_order_id=order_id)
            transaction.razorpay_payment_id = payment_id
            transaction.razorpay_signature = signature
            transaction.save()
            
            # Update Booking Status to COMPLETED automatically after payment
            booking = transaction.booking
            booking.status = 'completed'
            booking.final_price = transaction.amount
            booking.commission_kept = transaction.commission
            booking.provider_payout = transaction.payout
            booking.save()
            
            # Ensure provider returns to available (or stays available if not set to busy)
            provider = booking.provider
            provider.status = 'available'
            provider.save()
            
            messages.success(request, "Payment successful! Your booking has been completed.")
            return redirect('orders')
        except Exception as e:
            messages.error(request, f"Payment failed: {str(e)}")
            return redirect('orders')
    
    return redirect('home')

@login_required
def pay_via_upi(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        # Simulate UPI verification
        txn_id = request.POST.get('upi_txn_id')
        if txn_id:
            # Create Transaction record
            from decimal import Decimal
            total_price = booking.provider.price_per_hour
            commission = (total_price * Decimal('0.20')).quantize(Decimal('0.01'))
            payout = total_price - commission
            
            Transaction.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': total_price,
                    'commission': commission,
                    'payout': payout,
                    'payment_method': 'upi',
                    'transaction_id': f"UPI-{txn_id.upper()}"
                }
            )
            
            # Update Booking Status to COMPLETED automatically after payment
            booking.status = 'completed'
            booking.final_price = total_price
            booking.commission_kept = commission
            booking.provider_payout = payout
            booking.save()
            
            # Ensure provider stays available
            provider = booking.provider
            provider.status = 'available'
            provider.save()
            
            messages.success(request, f"UPI Payment Confirmed! Transaction ID: {txn_id}. Provider has been notified.")
            
            return render(request, 'payment_success.html', {
                'transaction_id': txn_id,
                'provider_name': f"{booking.provider.user.first_name} {booking.provider.user.last_name}",
                'amount': total_price
            })
        else:
            messages.error(request, "Please enter your UPI Transaction ID to confirm.")

    return render(request, 'pay_via_upi.html', {
        'booking': booking,
        'upi_id': settings.BUSINESS_UPI_ID
    })



