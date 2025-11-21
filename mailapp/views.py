from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import CustomUser, Email
from .mail_utils import generate_keys, fetch_inbox, send_local_email, decrypt_email

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")
        user = CustomUser.objects.create_user(username=email, email=email, password=password, first_name=name)
        generate_keys(user)
        return redirect("login")
    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("inbox")
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

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

    print(f"Found {len(inbox)} emails for {user.email}")  # Debug print

    return render(request, "inbox.html", {"inbox": inbox})


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


User = get_user_model()

@login_required
def compose_email_view(request):
    context = {}
    if request.method == "POST":
        sender = request.user  # assuming you are using Django auth
        recipient_emails = request.POST.get("to")
        subject = request.POST.get("subject")
        body = request.POST.get("body")

        # Generate keys for sender and recipients
        generate_keys(sender)
        for email in recipient_emails.split(","):
            try:
                recipient = CustomUser.objects.get(email=email.strip())
                generate_keys(recipient)
            except CustomUser.DoesNotExist:
                context["error"] = f"User '{email.strip()}' does not exist."
                return render(request, "compose.html", context)

        # Send encrypted email
        send_local_email(sender, recipient_emails, subject, body, is_encrypted=True)
        context["success"] = "Email sent successfully!"
        return render(request, "compose.html", context)

    return render(request, "compose.html", context)