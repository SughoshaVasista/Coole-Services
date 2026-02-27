from django.shortcuts import render, get_object_or_404, redirect
from .models import ServiceCategory, ServiceProvider, Booking
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
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

from django.db.models import Q, Avg, Count
from django.db.models.functions import Coalesce

def category_detail_view(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    
    # Calculate Category Mean (C) for Bayesian Average
    from django.db.models import Avg, Count
    from django.db.models.functions import Coalesce
    from .models import Booking
    
    cat_avg = Booking.objects.filter(
        provider__category=category,
        review_stars__isnull=False
    ).aggregate(cat_avg=Avg('review_stars'))['cat_avg'] or 0.0
    
    providers_qs = ServiceProvider.objects.filter(category=category, status='available').annotate(
        calculated_rating=Coalesce(Avg('bookings__review_stars'), 0.0),
        review_count=Count('bookings__review_stars')
    )
    
    # Dynamic Recommendation Algorithm (Bayesian Average)
    providers = list(providers_qs)
    M = 2 # minimum reviews threshold
    
    for p in providers:
        V = p.review_count
        R = p.calculated_rating
        C = cat_avg
        
        # Bayesian formula: (v / (v+m)) * R + (m / (v+m)) * C
        if V > 0:
            p.algorithm_score = ((V / (V + M)) * R) + ((M / (V + M)) * C)
        else:
            p.algorithm_score = 0.0
            
    # Sort providers dynamically by true algorithm score
    providers.sort(key=lambda x: (x.algorithm_score, x.review_count), reverse=True)
    
    top_recommended = None
    if providers and providers[0].algorithm_score >= 3.5 and providers[0].review_count > 0:
        top_recommended = providers[0]
        
    return render(request, 'category_detail.html', {'category': category, 'providers': providers, 'top_recommended': top_recommended})

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

        import random
        
        # Auto-Accept Logic: If provider is available, instantly assign them and generate OTP
        start_otp = str(random.randint(100000, 999999))
        
        booking = Booking.objects.create(
            user=request.user,
            provider=provider,
            booking_date=booking_date,
            service_location=request.POST.get('service_location', ''),
            notes=request.POST.get('notes', ''),
            status='accepted', # instantly accepted
            start_otp=start_otp
        )
        
        # Set provider to busy instantly
        provider.status = 'busy'
        provider.save()
        
        messages.success(request, f"Booking instantly confirmed! Your partner is assigned. Share OTP: {start_otp} when they arrive.")
        return redirect('orders') 

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
                import random
                booking.status = 'accepted'
                # Generate 6-digit OTP
                booking.start_otp = str(random.randint(100000, 999999))
                booking.save()
                # Ensure provider becomes busy
                provider.status = 'busy' 
                provider.save()
                messages.success(request, f"Job Accepted! OTP has been sent to the customer. When you reach, please enter the OTP to start work.")
            
            elif job_action == 'start_work':
                partner_otp = request.POST.get('start_otp', '').strip()
                if partner_otp == booking.start_otp:
                    booking.status = 'confirmed'
                    booking.save()
                    messages.success(request, "OTP Verified! Work has officially started.")
                else:
                    messages.error(request, "Invalid OTP. Please ask the customer for the correct code.")

            elif job_action == 'mark_done':
                # Service is done, now awaiting payment
                booking.status = 'service_done'
                booking.save()
                messages.success(request, "Service marked as Done! Awaiting client payment.")

            elif job_action == 'verify_payment':
                partner_input_id = request.POST.get('partner_txn_id', '').strip().upper()
                transaction = getattr(booking, 'transaction', None)
                
                # Security Check: Ensure the ID matches what the customer submitted
                # Customer ID is stored as "UPI-XXXXXX"
                stored_id = transaction.transaction_id if transaction else ""
                
                # Check if matches exactly or matches the unique part (suffix)
                if not transaction or (partner_input_id not in stored_id and stored_id not in f"UPI-{partner_input_id}"):
                    messages.error(request, f"Verification Failed: The Transaction ID '{partner_input_id}' does NOT match our records for this booking.")
                    return redirect('partner_dashboard')

                # If matches, proceed with finalization
                from decimal import Decimal
                COMMISSION_RATE = Decimal('0.20')
                
                final_price = booking.final_price if booking.final_price else provider.price_per_hour
                commission = (final_price * COMMISSION_RATE).quantize(Decimal('0.01'))
                payout = final_price - commission
                
                booking.status = 'completed'
                booking.commission_kept = commission
                booking.provider_payout = payout
                booking.save()
                
                # Update transaction details with final verified payout
                transaction.commission = commission
                transaction.payout = payout
                transaction.save()

                # Free up the provider
                provider.status = 'available'
                provider.save()
                messages.success(request, f"Payment Verified Successfully! UTR: {partner_input_id}. ₹{payout} has been credited to your balance.")

            elif job_action == 'complete':
                # Fallback or legacy complete logic
                booking.status = 'completed'
                booking.save()
                provider.status = 'available'
                provider.save()
                messages.success(request, "Booking finalized.")
            
            elif job_action == 'reject':

                booking.status = 'cancelled'
                booking.save()
                # Free up the provider
                provider.status = 'available'
                provider.save()
                messages.warning(request, "Job Rejected. You are now available for other bookings.")

        return redirect('partner_dashboard')

    # Fetch jobs by status
    incoming_requests = Booking.objects.filter(provider=provider, status='pending').order_by('booking_date')
    active_jobs = Booking.objects.filter(provider=provider, status__in=['accepted', 'confirmed']).order_by('booking_date')
    unpaid_jobs = Booking.objects.filter(provider=provider, status='service_done').order_by('booking_date')
    verification_pending = Booking.objects.filter(provider=provider, status='paid').order_by('booking_date')
    completed_jobs = Booking.objects.filter(provider=provider, status='completed').select_related('transaction').order_by('-booking_date')[:5]

    context = {
        'provider': provider,
        'incoming_requests': incoming_requests,
        'active_jobs': active_jobs,
        'unpaid_jobs': unpaid_jobs,
        'verification_pending': verification_pending,
        'completed_jobs': completed_jobs
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partner_dashboard_partial.html', context)

    return render(request, 'partner_dashboard.html', context)

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
            
            # Update Booking Status to PAID after payment (Awaiting Provider Acceptance)
            booking = transaction.booking
            booking.status = 'paid'
            booking.final_price = transaction.amount
            booking.commission_kept = transaction.commission
            booking.provider_payout = transaction.payout
            booking.save()
            
            # Keep provider available for now until they accept
            provider = booking.provider
            provider.save()
            
            messages.success(request, "Payment successful! Your booking is now awaiting provider acceptance.")
            return redirect('orders')
        except Exception as e:
            messages.error(request, f"Payment failed: {str(e)}")
            return redirect('orders')
    
    return redirect('home')

@login_required
def pay_via_upi(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Initialize Razorpay Client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Calculate amount in paise
    amount = int(booking.provider.price_per_hour * 100)
    
    # Create Razorpay Order specifying UPI preference if possible, standard order is fine
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1',
        'notes': {
            'booking_id': str(booking.id),
            'method': 'upi'
        }
    }
    
    try:
        razorpay_order = client.order.create(data=order_data)
        
        # Calculate commission and payout
        from decimal import Decimal
        total_price = booking.provider.price_per_hour
        commission = (total_price * Decimal('0.20')).quantize(Decimal('0.01'))
        payout = total_price - commission
        
        # Update or Create Transaction Reference
        transaction, created = Transaction.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': total_price,
                'commission': commission,
                'payout': payout,
                'payment_method': 'upi',
                'razorpay_order_id': razorpay_order['id']
            }
        )
        
        if not created:
            transaction.razorpay_order_id = razorpay_order['id']
            transaction.payment_method = 'upi'
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
        
        return render(request, 'pay_via_upi.html', context)
        
    except Exception as e:
        messages.error(request, f"Error initializing UPI secure tunnel: {str(e)}")
        return redirect('orders')

@login_required
def rebook_view(request, booking_id):
    """Takes an old booking and redirects to the provider page with pre-filled details"""
    old_booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    provider_id = old_booking.provider.id
    
    # We use query parameters to pass the old details to the provider detail page
    from django.utils.http import urlencode
    params = urlencode({
        'notes': old_booking.notes,
        'location': old_booking.service_location
    })
    
    return redirect(f'/services/provider/{provider_id}/?{params}')


def view_receipt(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)
    
    # Optional: Only allow the customer who booked or the provider to see the receipt
    if request.user != booking.user and (not request.user.service_provider or request.user.service_provider != booking.provider):
        messages.error(request, "Access Denied.")
        return redirect('home')
        
    import random
    quotes = [
        "Quality is not an act, it is a habit. - Aristotle",
        "The best way to find yourself is to lose yourself in the service of others. - Mahatma Gandhi",
        "Service to others is the rent you pay for your room here on earth. - Muhammad Ali",
        "Quality is remembered long after the price is forgotten. - Gucci Family",
        "Success is not the key to happiness. Happiness is the key to success. - Albert Schweitzer"
    ]
    random_quote = random.choice(quotes)
    
    # Calculate tax and total for breakdown
    base_price = booking.final_price or booking.provider.price_per_hour
    tax_rate = Decimal('0.18') # 18% GST simulation
    tax_amount = (base_price * tax_rate).quantize(Decimal('0.01'))
    service_charge = Decimal('50.00')
    grand_total = base_price + tax_amount + service_charge
    
    return render(request, 'receipt.html', {
        'booking': booking,
        'random_quote': random_quote,
        'base_price': base_price,
        'tax_amount': tax_amount,
        'service_charge': service_charge,
        'grand_total': grand_total,
        'invoice_id': f"INV-{uuid.uuid4().hex[:8].upper()}"
    })

import hmac
import hashlib
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def razorpay_webhook(request):
    """
    Listens for 'payment.captured' events directly from Razorpay's servers.
    This guarantees auto-confirmation even if the user closes their browser
    during the payment redirect.
    """
    if request.method == 'POST':
        try:
            payload = request.body.decode('utf-8')
            signature = request.headers.get('X-Razorpay-Signature')
            secret = settings.RAZORPAY_WEBHOOK_SECRET

            # Calculate the expected signature using HMAC-SHA256
            expected_signature = hmac.new(
                bytes(secret, 'utf-8'),
                msg=bytes(payload, 'utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()

            # Verify Webhook Authenticity
            if not hmac.compare_digest(expected_signature, signature):
                return HttpResponse(status=400)
            
            # Parse the event
            event = json.loads(payload)
            if event['event'] == 'payment.captured':
                payment_entity = event['payload']['payment']['entity']
                
                # Razorpay allows passing custom notes during payment creation.
                # We expect 'booking_id' to be passed in those notes.
                booking_id = payment_entity.get('notes', {}).get('booking_id')
                
                if booking_id:
                    booking = Booking.objects.get(id=booking_id)
                    transaction = getattr(booking, 'transaction', None)
                    
                    if transaction and booking.status != 'completed':
                        provider = booking.provider
                        final_price = booking.final_price if booking.final_price else provider.price_per_hour
                        
                        from decimal import Decimal
                        COMMISSION_RATE = Decimal('0.20')
                        commission = (final_price * COMMISSION_RATE).quantize(Decimal('0.01'))
                        payout = final_price - commission
                        
                        # --- Auto-Confirm the Transaction ---
                        booking.status = 'completed'
                        booking.commission_kept = commission
                        booking.provider_payout = payout
                        booking.save()
                        
                        transaction.commission = commission
                        transaction.payout = payout
                        transaction.transaction_id = payment_entity.get('id') # The actual Razorpay Pay ID
                        transaction.payment_method = 'razorpay'
                        transaction.save()
                        
                        # Free up the provider automatically
                        provider.status = 'available'
                        provider.save()

            return HttpResponse(status=200)
            
        except Exception as e:
            print(f"Webhook Error: {e}")
            return HttpResponse(status=400)
            
    return HttpResponse(status=405)
