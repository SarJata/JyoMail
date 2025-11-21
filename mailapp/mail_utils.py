import pgpy
from .models import Email, CustomUser
from pathlib import Path

KEYS_DIR = Path("keys")
KEYS_DIR.mkdir(exist_ok=True)


def generate_keys(user: CustomUser):
    """Generate PGP keys for a user if they don't already exist, and store in the model."""
    if user.pgp_private_key and user.pgp_public_key:
        return user.pgp_public_key, user.pgp_private_key

    key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = pgpy.PGPUID.new(user.email)
    key.add_uid(
        uid,
        usage={pgpy.constants.KeyFlags.Sign, pgpy.constants.KeyFlags.EncryptCommunications},
        hashes=[pgpy.constants.HashAlgorithm.SHA256],
        ciphers=[pgpy.constants.SymmetricKeyAlgorithm.AES256],
        compression=[pgpy.constants.CompressionAlgorithm.ZLIB]
    )

    user.pgp_public_key = str(key.pubkey)
    user.pgp_private_key = str(key)
    user.save()
    return user.pgp_public_key, user.pgp_private_key


def encrypt_email(body: str, recipient: CustomUser) -> str:
    public_key = pgpy.PGPKey.from_blob(recipient.pgp_public_key)[0]
    message = pgpy.PGPMessage.new(body)
    encrypted_message = public_key.encrypt(message)
    return str(encrypted_message)


def decrypt_email(encrypted_body: str, user: CustomUser) -> str:
    private_key = pgpy.PGPKey.from_blob(user.pgp_private_key)[0]
    message = pgpy.PGPMessage.from_blob(encrypted_body)
    return private_key.decrypt(message).message


def send_local_email(sender, recipient_email, subject, body, is_encrypted=False):
    """
    Send an email to a single recipient and save it to the database.
    If encrypt=True, the body will be encrypted with recipient's public key.
    """
    try:
        recipient = CustomUser.objects.get(email=recipient_email)
    except CustomUser.DoesNotExist:
        print(f"Recipient {recipient_email} does not exist.")
        return False

    if is_encrypted:
        body = encrypt_email(body, recipient)

    # Save email to the database
    Email.objects.create(
        sender=sender.email,
        recipients=recipient.email,
        subject=subject,
        body=body,
        is_encrypted=is_encrypted
    )
    return True

def fetch_inbox(user: CustomUser):
    from .models import Email

    print(f"[DEBUG] Fetching inbox for user: {user.email}")

    # Print all emails in the database for debugging
    all_emails = Email.objects.all().values("id", "sender", "recipients", "subject", "is_encrypted")
    print("[DEBUG] All emails in DB:")
    for e in all_emails:
        print(e)

    # Fetch emails where recipient exactly matches user email
    emails = Email.objects.filter(recipients=user.email).order_by('-timestamp')
    print(f"[DEBUG] Emails found for user {user.email}: {emails.count()}")

    inbox = []
    for mail in emails:
        body = mail.body
        if mail.is_encrypted:
            try:
                body = decrypt_email(mail.body, user)
            except Exception as e:
                body = f"[Encrypted email – cannot decrypt: {e}]"

        inbox.append({
            "id": mail.id,
            "from": mail.sender,
            "to": mail.recipients,
            "subject": mail.subject,
            "body": body,
            "timestamp": mail.timestamp,
            "is_read": mail.is_read
        })

    print(f"[DEBUG] Inbox built with {len(inbox)} emails")
    return inbox
