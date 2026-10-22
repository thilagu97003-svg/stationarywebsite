import re

from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import ContactMessage, Order

PHONE_RE = r"[6-9]\d{9}"


def _style(form, placeholders=None):
    for name, field in form.fields.items():
        if not isinstance(field.widget, (forms.RadioSelect,)):
            field.widget.attrs.setdefault("class", "field")
        if placeholders and name in placeholders:
            field.widget.attrs["placeholder"] = placeholders[name]


class SigninForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self, {"username": "User name", "password": "Password"})
        self.fields["username"].widget.attrs.update(autocomplete="username", autofocus=True)
        self.fields["password"].widget.attrs.update(autocomplete="current-password")


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self, {
            "username": "User name",
            "email": "Email ID",
            "password": "Password",
            "confirm_password": "Confirm Password",
        })
        self.fields["username"].widget.attrs.update(autocomplete="username", minlength=3, autofocus=True)
        self.fields["email"].widget.attrs.update(autocomplete="email")
        self.fields["password"].widget.attrs.update(autocomplete="new-password", minlength=8)
        self.fields["confirm_password"].widget.attrs.update(autocomplete="new-password", minlength=8)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if "." not in email.rsplit("@", 1)[-1]:
            raise forms.ValidationError("Enter a valid email address, e.g. name@example.com.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists. Sign in or reset your password.")
        return email

    def clean_password(self):
        pwd = self.cleaned_data["password"]
        user = User(username=self.cleaned_data.get("username", ""), email=self.cleaned_data.get("email", ""))
        validate_password(pwd, user)   # rules come from AUTH_PASSWORD_VALIDATORS in settings.py
        return pwd

    def clean(self):
        data = super().clean()
        pwd, cpwd = data.get("password"), data.get("confirm_password")
        if pwd and cpwd and pwd != cpwd:
            self.add_error("confirm_password", "Passwords do not match.")
        return data


# ---- Forgot password (styled versions of Django's built-in forms)
class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self, {"email": "Registered Email ID"})


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self, {"new_password1": "New password", "new_password2": "Confirm new password"})


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "address", "city", "postal_code", "payment_method"]
        labels = {"name": "Name", "address": "Street Address", "city": "Town/City", "postal_code": "Postal Code"}
        widgets = {"payment_method": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)
        self.fields["postal_code"].widget.attrs.update(inputmode="numeric", maxlength=7)

    def clean_postal_code(self):
        code = self.cleaned_data["postal_code"].replace(" ", "")
        if not re.fullmatch(r"\d{6}", code):
            raise forms.ValidationError("Enter a 6-digit postal code.")
        return code


class ContactForm(forms.ModelForm):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 1}))

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self, {
            "name": "Enter your Name", 
            "email": "Enter Email ID", 
            "phone": "Enter your number", 
            "message": "Enter Message"
        })
        self.fields["phone"].widget.attrs.update(maxlength="10", inputmode="numeric")

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        if not re.fullmatch(r"[a-zA-Z\s]+", name):
            raise forms.ValidationError("Name should only contain letters and spaces.")
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 letters.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").replace(" ", "").strip()
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        if not re.fullmatch(r"\d{10}", phone):
            raise forms.ValidationError("Phone number must contain exactly 10 digits.")
        return phone

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if not message:
            raise forms.ValidationError("Message box cannot be empty.")
        return message


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(choices=[(i, i) for i in range(5, 0, -1)], widget=forms.RadioSelect)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3, "class": "field", "placeholder": "Write your review (optional)"}))