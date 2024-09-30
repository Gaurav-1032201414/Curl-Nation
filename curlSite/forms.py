from django import forms
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'email', 'full_name', 'sync_to_shopify', 'sync_to_other_source']

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']