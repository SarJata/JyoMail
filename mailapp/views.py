from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import CustomUser, Email
from .mail_utils import generate_keys, fetch_inbox, send_local_email, decrypt_email
from .forms import SignupForm, LoginForm, ComposeForm

User = get_user_model()

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            generate_keys(user)
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("inbox")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def inbox_view(request):
    user = request.user
    # Fetch emails where recipients exactly match the logged-in user's email
    emails = Email.objects.filter(recipients__iexact=user.email).order_by('-timestamp')

    inbox = []

    for mail in emails:
        body = mail.body
        if mail.is_encrypted:
            try:
                body = decrypt_email(mail.body, user)
            except Exception as e:
                # If decryption fails, show a placeholder
                body = f"[Encrypted – cannot decrypt: {e}]"

        inbox.append({
            "id": mail.id,
            "from": mail.sender,
            "to": mail.recipients,
            "subject": mail.subject,
            "body": body,
            "timestamp": mail.timestamp,
            "is_read": mail.is_read,
        })

    return render(request, "inbox.html", {"inbox": inbox})

@login_required
def sent_view(request):
    user = request.user
    # Fetch emails where sender matches the logged-in user's email
    emails = Email.objects.filter(sender__iexact=user.email).order_by('-timestamp')

    sent_box = []

    for mail in emails:
        body = mail.body
        # Decrypt if possible (though sender usually has the key, we'll keep logic consistent)
        if mail.is_encrypted:
            try:
                body = decrypt_email(mail.body, user)
            except Exception as e:
                body = f"[Encrypted – cannot decrypt: {e}]"

        sent_box.append({
            "id": mail.id,
            "from": mail.sender,
            "to": mail.recipients,
            "subject": mail.subject,
            "body": body,
            "timestamp": mail.timestamp,
            "is_read": True,
        })

    return render(request, "sent.html", {"inbox": sent_box})

def email_detail_view(request, email_id):
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    email = get_object_or_404(Email, id=email_id)
    body = email.body
    if email.is_encrypted:
        try:
            body = decrypt_email(body, user)
        except Exception as e:
            body = f"[Encrypted email – cannot decrypt: {e}]"

    return render(request, "email_detail.html", {
        "email": {
            "id": email.id,
            "sender": email.sender,
            "recipients": email.recipients,
            "subject": email.subject,
            "body": body,
            "is_read": email.is_read
        }
    })

@login_required
def compose_email_view(request):
    context = {}
    if request.method == "POST":
        form = ComposeForm(request.POST)
        if form.is_valid():
            sender = request.user
            recipient_emails = form.cleaned_data["recipients"]
            subject = form.cleaned_data["subject"]
            body = form.cleaned_data["body"]

            # Generate keys for sender and recipients
            generate_keys(sender)
            for email in recipient_emails.split(","):
                try:
                    recipient = CustomUser.objects.get(email=email.strip())
                    generate_keys(recipient)
                except CustomUser.DoesNotExist:
                    form.add_error("recipients", f"User '{email.strip()}' does not exist.")
                    return render(request, "compose.html", {"form": form})

            # Send encrypted email
            send_local_email(sender, recipient_emails, subject, body, is_encrypted=True)
            context["success"] = "Email sent successfully!"
            form = ComposeForm() # Reset form
            context["form"] = form
            return render(request, "compose.html", context)
        else:
            context["form"] = form
            return render(request, "compose.html", context)
    else:
        form = ComposeForm()
    
    context["form"] = form
    return render(request, "compose.html", context)