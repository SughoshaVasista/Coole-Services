from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from services.models import Booking
from django.contrib import messages
from services.models import ServiceProvider

@login_required
def order_list_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    context = {'bookings': bookings}
    
    if request.headers.get('HX-Request'):
        return render(request, 'orders_partial.html', context)
        
    return render(request, 'orders.html', context)

@login_required
@require_POST
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        
        # Free up the provider
        provider = booking.provider
        provider.status = 'available'
        provider.save()
        
        messages.success(request, f"Booking #{booking.id} cancelled successfully and provider is now available.")
    else:
        messages.error(request, "Only pending bookings can be cancelled.")
    return redirect('orders')

@login_required
@require_POST
def complete_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    # Typically provider completes, but user confirmation might be nice.
    # For now, let's say provider does it, or user confirms it if provider marked it 'completed' but user disputes?
    # Simple logic: User confirms completion if status is Confirmed? No, usually provider marks complete.
    # Let's say user can mark complete if they are satisfied.
    if booking.status == 'confirmed':
        booking.status = 'completed'
        booking.save()
        messages.success(request, f"Booking #{booking.id} marked as completed.")
    else:
        messages.error(request, "Only confirmed bookings can be completed.")
    return redirect('orders')

@login_required
@require_POST
def submit_review_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != 'completed':
        messages.error(request, "You can only review completed bookings.")
        return redirect('orders')

    rating = request.POST.get('rating')
    review_text = request.POST.get('review_text')

    if rating:
        try:
             # Validate rating
            rating_val = int(rating)
            if 1 <= rating_val <= 5:
                booking.review_stars = rating_val
                booking.review_text = review_text
                booking.save()
                
                # Update Provider Rating logic (simple average)
                provider = booking.provider
                # Recalculate average
                # This could be optimized but works for now
                bookings = Booking.objects.filter(provider=provider, review_stars__isnull=False)
                count = bookings.count()
                total = sum([b.review_stars for b in bookings])
                if count > 0:
                    provider.rating = round(total / count, 1)
                    provider.save()

                messages.success(request, "Review submitted successfully!")
            else:
                messages.error(request, "Invalid rating value.")
        except ValueError:
             messages.error(request, "Invalid rating format.")
    
    return redirect('orders')
