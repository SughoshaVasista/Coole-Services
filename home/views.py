from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from .models import ContactSubmission
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from profiles.models import UserProfile
from services.models import ServiceProvider, ServiceCategory
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce

def home_view(request):
    return render(request, 'landing.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Basic validation
        if not name or not email or not message_text:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'contact.html', {
                'form_data': {
                    'name': name,
                    'email': email,
                    'subject': subject,
                    'message': message_text,
                }
            })

        # Save to database
        ContactSubmission.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_text,
        )
        messages.success(request, "Thank you! Your message has been sent successfully. We'll get back to you soon.")
        return redirect('contact')

    return render(request, 'contact.html')
 
 
def signup_selection_view(request):
    if request.user.is_authenticated:
        try:
            getattr(request.user, 'service_provider')
            return redirect('partner_dashboard')
        except AttributeError:
            return redirect('home')
    return render(request, 'signup_selection.html')


def login_selection_view(request):
    if request.user.is_authenticated:
        try:
            getattr(request.user, 'service_provider')
            return redirect('partner_dashboard')
        except AttributeError:
            return redirect('home')
    return render(request, 'login_selection.html')


def login_view(request):
    if request.user.is_authenticated:
        # If already logged in, send to their respective dashboard
        try:
            getattr(request.user, 'service_provider')
            return redirect('partner_dashboard')
        except AttributeError:
            return redirect('home')

    role_pref = request.GET.get('role', 'customer')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Security Check: Does the user role match the intended login page?
                is_provider = False
                try:
                    getattr(user, 'service_provider')
                    is_provider = True
                except AttributeError:
                    is_provider = False

                if role_pref == 'partner' and not is_provider:
                    messages.error(request, "This account is not a Partner account. Please use Customer Login.")
                    return redirect(f"{request.path}?role=customer")
                
                if role_pref == 'customer' and is_provider:
                    messages.error(request, "This is a Partner account. Please use Partner Login.")
                    return redirect(f"{request.path}?role=partner")

                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                
                # Assign different localhost (ports) for simulation
                PARTNER_BASE = "http://127.0.0.1:8001"
                CUSTOMER_BASE = "http://127.0.0.1:8000"

                if is_provider:
                    from django.urls import reverse
                    target_path = reverse('partner_dashboard')
                    return redirect(f"{PARTNER_BASE}{target_path}")
                else:
                    from django.urls import reverse
                    target_path = reverse('home')
                    param_next = request.GET.get('next') or request.POST.get('next')
                    if param_next:
                        target_path = param_next
                    return redirect(f"{CUSTOMER_BASE}{target_path}")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'role': role_pref})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    role = request.GET.get('role', 'customer')
    from .forms import PartnerSignUpForm, SignUpForm
    
    FormClass = PartnerSignUpForm if role == 'partner' else SignUpForm

    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Assign different localhost (ports)
            PARTNER_BASE = "http://127.0.0.1:8001"
            CUSTOMER_BASE = "http://127.0.0.1:8000"

            if role == 'partner':
                from django.urls import reverse
                messages.success(request, "Partner account created! Welcome to the team.")
                return redirect(f"{PARTNER_BASE}{reverse('partner_dashboard')}")
            else:
                from django.urls import reverse
                messages.success(request, "Account created successfully! Welcome to Cool-E.")
                return redirect(f"{CUSTOMER_BASE}{reverse('home')}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FormClass()
    
    return render(request, 'signup.html', {'form': form, 'role': role})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("home")


def terms_view(request):
    return render(request, 'terms.html')


def about_view(request):
    return render(request, 'about.html')


def forgot_password_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        
        # Search in UserProfile and ServiceProvider
        user = None
        
        # Check UserProfile (Customers)
        profile = UserProfile.objects.filter(phone_number=phone).first()
        if profile:
            user = profile.user
        else:
            # Check ServiceProvider (Partners)
            provider = ServiceProvider.objects.filter(contact_number=phone).first()
            if provider:
                user = provider.user
        
        if user:
            # For simulation, we'll store the user ID in session and redirect to reset page
            request.session['reset_user_id'] = user.id
            messages.success(request, f"User found! Please set your new password for {user.username}.")
            return redirect('reset_password_phone')
        else:
            messages.error(request, "No account found with this phone number.")
            
    return render(request, 'forgot_password.html')


def reset_password_phone_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Please start the password reset process again.")
        return redirect('forgot_password')
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.set_password(new_password)
            user.save()
            # Clear session
            del request.session['reset_user_id']
            messages.success(request, "Password has been reset successfully! Please log in with your new password.")
            return redirect('login')
            
    return render(request, 'reset_password_phone.html', {'reset_user': user})

def recommendations_view(request):
    categories = ServiceCategory.objects.all()
    top_providers_by_category = []
    
    from django.db.models import Avg, Count
    from django.db.models.functions import Coalesce
    from services.models import Booking

    for category in categories:
        # Calculate Category Mean (C) dynamically per loop
        cat_avg = Booking.objects.filter(
            provider__category=category,
            review_stars__isnull=False
        ).aggregate(cat_avg=Avg('review_stars'))['cat_avg'] or 0.0

        providers_qs = ServiceProvider.objects.filter(category=category, status='available').annotate(
            calculated_rating=Coalesce(Avg('bookings__review_stars'), 0.0),
            review_count=Count('bookings__review_stars')
        )
        
        providers = list(providers_qs)
        M = 2  # minimum reviews threshold
        
        for p in providers:
            V = p.review_count
            R = p.calculated_rating
            C = cat_avg
            
            # Dynamic Recommendation Bayeisan Score: (v / (v+m)) * R + (m / (v+m)) * C
            if V > 0:
                p.algorithm_score = ((V / (V + M)) * R) + ((M / (V + M)) * C)
            else:
                p.algorithm_score = 0.0
                
        # Sort providers dynamically by true algorithm score evaluated within their category context
        providers.sort(key=lambda x: (x.algorithm_score, x.review_count), reverse=True)

        if providers and providers[0].algorithm_score >= 3.5 and providers[0].review_count > 0:
            top_providers_by_category.append({
                'category': category,
                'provider': providers[0],
                'algorithm_score': providers[0].algorithm_score
            })

    # Sort the final list to show absolute highest rated first overall based on our dynamic engine
    top_providers_by_category.sort(key=lambda x: x['algorithm_score'], reverse=True)

    # Personalized Recommendation Logic
    personalized_rec = None
    if request.user.is_authenticated:
        last_booking = Booking.objects.filter(user=request.user).order_by('-booking_date').first()
        if last_booking and last_booking.provider.category:
            last_category = last_booking.provider.category
            # Find the best provider in a DIFFERENT category to cross-sell
            for rec in top_providers_by_category:
                if rec['category'] != last_category:
                    personalized_rec = {
                        'reason_category': last_category.name,
                        'data': rec
                    }
                    # Remove it from the main list so it doesn't duplicate
                    top_providers_by_category.remove(rec)
                    break

    return render(request, 'recommendations.html', {
        'recommended_list': top_providers_by_category,
        'personalized_rec': personalized_rec
    })
