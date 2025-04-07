from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserForm(forms.ModelForm):
    """Form for updating user information."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

class ProfileForm(forms.ModelForm):
    """Form for updating profile information."""
    class Meta:
        model = Profile
        fields = ['bio', 'profile_image', 'website', 'social_github', 
                 'social_twitter', 'social_linkedin', 'social_instagram']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs.update({'class': 'form-control', 'rows': 4})
        self.fields['profile_image'].widget.attrs.update({'class': 'form-control'})
        self.fields['website'].widget.attrs.update({'class': 'form-control'})
        self.fields['social_github'].widget.attrs.update({'class': 'form-control'})
        self.fields['social_twitter'].widget.attrs.update({'class': 'form-control'})
        self.fields['social_linkedin'].widget.attrs.update({'class': 'form-control'})
        self.fields['social_instagram'].widget.attrs.update({'class': 'form-control'})
