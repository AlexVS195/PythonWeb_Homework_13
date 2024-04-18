from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from quotes.models import Author
from .models import Quote

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.',
                code='invalid_username'
            )
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    pass

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']

class QuoteForm(forms.ModelForm):
    tags = forms.CharField(label='Tags', required=False)

    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']

class ScrapeForm(forms.Form):
    url = forms.URLField(label='URL address')