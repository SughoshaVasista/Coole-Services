from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from .models import ContactSubmission
from django.contrib import messages
from django.views.decorators.http import require_POST


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


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                # Redirect to 'next' param if present, otherwise home
                next_url = request.GET.get('next') or request.POST.get('next') or 'home'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Cool-E.")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("home")


def terms_view(request):
    return render(request, 'terms.html')


def about_view(request):
    return render(request, 'about.html')
