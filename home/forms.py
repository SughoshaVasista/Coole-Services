from django import forms
from django.contrib.auth.models import User
from profiles.models import UserProfile

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Profile is created by signal, so we just update it
            if hasattr(user, 'userprofile'):
                profile = user.userprofile
                profile.phone_number = self.cleaned_data.get('phone_number', '')
                profile.address = self.cleaned_data.get('address', '')
                profile.save()
        return user

from services.models import ServiceCategory, ServiceProvider
import uuid

class PartnerSignUpForm(SignUpForm):
    category = forms.ModelChoiceField(queryset=ServiceCategory.objects.all(), required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)
    price_per_hour = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    age = forms.IntegerField(required=True)
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    current_location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. Kondapur, Hyderabad'}))

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Create ServiceProvider entry
            ServiceProvider.objects.create(
                user=user,
                category=self.cleaned_data['category'],
                description=self.cleaned_data['description'],
                price_per_hour=self.cleaned_data['price_per_hour'],
                age=self.cleaned_data['age'],
                contact_number=self.cleaned_data.get('phone_number', ''),
                address=self.cleaned_data.get('address', ''),
                latitude=self.cleaned_data.get('latitude'),
                longitude=self.cleaned_data.get('longitude'),
                current_location=self.cleaned_data.get('current_location', ''),
                service_code=f"PRO-{uuid.uuid4().hex[:6].upper()}",
                status='available'
            )
        return user
