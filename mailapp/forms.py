from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()

class SignupForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    name = forms.CharField(required=True, label="Full Name")

    class Meta:
        model = User
        fields = ["email", "password", "name"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["name"]
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}), label="Email Address")

class ComposeForm(forms.Form):
    recipients = forms.CharField(label="To", widget=forms.TextInput(attrs={'placeholder': 'recipient@example.com'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "What's this about?"}))
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 12, 'placeholder': 'Write your message here...'}), label="Message")
