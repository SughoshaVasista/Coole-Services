from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UserProfile
from services.models import ServiceProvider, Booking
from django.contrib import messages

def is_provider(user):
    return hasattr(user, 'service_provider')

@login_required
def profile_view(request):
    user = request.user
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Check if user is a provider
    is_prov = is_provider(user)
    provider_details = user.service_provider if is_prov else None
    
    # Get bookings where user is the customer
    user_bookings = Booking.objects.filter(user=user).order_by('-booking_date')
    
    # Get bookings where user is the provider
    provider_bookings = Booking.objects.filter(provider__user=user).order_by('-booking_date') if is_prov else None

    if request.method == 'POST':
        # Identify if this is a profile update or a booking action
        action = request.POST.get('action') 
        
        if action == 'update_profile':
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            profile.phone_number = request.POST.get('phone_number', profile.phone_number)
            profile.address = request.POST.get('address', profile.address)
            profile.current_location = request.POST.get('current_location', profile.current_location)
            
            if 'profile_picture' in request.FILES:
                # Basic validation or image processing could be added here
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profiles')

        elif action == 'update_booking_status':
            # Provider managing a booking
            if not is_prov:
                messages.error(request, "Unauthorized action.")
                return redirect('profiles')
                
            booking_id = request.POST.get('booking_id')
            new_status = request.POST.get('status')
            
            booking = get_object_or_404(Booking, id=booking_id, provider__user=user)
            
            if new_status in ['confirmed', 'completed', 'cancelled']:
                booking.status = new_status
                booking.save()
                
                # Sync Provider availability for Uber model logic
                if new_status in ['completed', 'cancelled']:
                    booking.provider.status = 'available'
                    booking.provider.save()
                    
                messages.success(request, f"Booking status updated to {new_status}.")
            else:
                 messages.error(request, "Invalid status update.")
            
            return redirect('profiles')

    context = {
        'profile': profile,
        'is_provider': is_prov,
        'provider_details': provider_details,
        'user_bookings': user_bookings,
        'provider_bookings': provider_bookings
    }
    return render(request, 'profiles.html', context)
