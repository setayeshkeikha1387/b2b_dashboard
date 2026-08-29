"""Forms for the accounts app.

`SignupForm` is written from scratch rather than subclassing Django's
`UserCreationForm`, because that form hard-codes assumptions about a
`username` field that our email-only `User` model doesn't have.
"""
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm

from apps.accounts.models import User


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm password", widget=forms.PasswordInput, strip=False,
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "job_title"]

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        if password1:
            password_validation.validate_password(password1)
        return password2

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "job_title"]


class EmailPasswordResetForm(PasswordResetForm):
    """Thin wrapper kept for a single, explicit import path in urls.py —
    behaves exactly like Django's built-in form, which already works
    correctly with an email-only USERNAME_FIELD."""
