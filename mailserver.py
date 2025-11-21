#!/usr/bin/env python
"""
Local mailserver-ish CLI utility.
Usage:
  python mailserver.py
It will print messages in the DB and let you type `send` to create a test message.
This is optional — primary web interface is the Django app.
"""
import os
import sys
import django
import time

# ensure this file is run from the project root (one level above manage.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "postguard.settings")
django.setup()

from mailapp.models import Email

def show_inbox():
    print("\n=== All local emails (latest first) ===")
    for m in Email.objects.all().order_by("-timestamp")[:50]:
        print(f"[{m.id}] {m.timestamp} | from={m.sender} to={m.recipients} subj={m.subject}")

def create_test_email():
    sender = input("From (e.g. alice@jyomail): ").strip() or "alice@jyomail"
    to = input("To (comma separated): ").strip() or "bob@jyomail"
    subject = input("Subject: ").strip() or "Hello"
    body = input("Body: ").strip() or "Test body"
    e = Email.objects.create(sender=sender, recipients=to, subject=subject, body=body)
    print("Created email id", e.id)

def print_email_details():
    eid = input("Email id to view: ").strip()
    if not eid.isdigit():
        print("Invalid id")
        return
    try:
        m = Email.objects.get(id=int(eid))
    except Email.DoesNotExist:
        print("No such email")
        return
    print("----")
    print("From:", m.sender)
    print("To:", m.recipients)
    print("Subject:", m.subject)
    print("Body:\n", m.body)
    print("----")

def main():
    print("Mailserver CLI (local DB). Type 'help' for commands.")
    try:
        while True:
            cmd = input("\nCommand (list / view / new / exit / help): ").strip().lower()
            if cmd in ("exit", "quit"):
                break
            if cmd == "list":
                show_inbox()
            elif cmd == "new":
                create_test_email()
            elif cmd == "view":
                print_email_details()
            elif cmd == "help":
                print("Commands: list, view, new, exit")
            else:
                print("Unknown command:", cmd)
    except KeyboardInterrupt:
        print("\nStopping.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
