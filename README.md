# JyoMail (PostGuard)

JyoMail is a secure, local-first email application built with Django. It features PGP encryption for secure communication, a custom user model with key management, and a local mail server simulation.

## Features

- **Secure Communication**: Built-in PGP encryption and decryption for emails.
- **Local Mail Server**: Simulates email sending and receiving locally without external SMTP servers.
- **User Management**: Custom user model supporting PGP key generation and storage.
- **Web Interface**:
    - **Inbox**: View received emails with automatic decryption.
    - **Sent**: View sent emails.
    - **Compose**: Send encrypted emails to other local users.
- **CLI Utility**: `mailserver.py` for interacting with the local mail database via command line.

## Tech Stack

- **Backend**: Python, Django
- **Database**: SQLite (default)
- **Encryption**: PGPy
- **Frontend**: HTML, CSS (Django Templates)

## Prerequisites

- Python 3.8+
- pip

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd JyoMail
    ```

2.  **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (optional, for admin access):**
    ```bash
    python manage.py createsuperuser
    ```

## Usage

### Running the Web Application

1.  Start the Django development server:
    ```bash
    python manage.py runserver
    ```

2.  Open your browser and navigate to `http://127.0.0.1:8000/`.

3.  **Sign Up / Login**: Create a new account. PGP keys will be automatically generated for you upon signup.

4.  **Send Emails**: Use the "Compose" feature to send emails to other registered users. Emails are encrypted before storage.

### Using the CLI Mail Server

You can also interact with the mail storage using the provided CLI script.

1.  Run the mail server script:
    ```bash
    python mailserver.py
    ```

2.  Available commands:
    - `list`: Show all local emails.
    - `view`: View details of a specific email by ID.
    - `new`: Create a test email interactively.
    - `exit`: Quit the CLI.

## Project Structure

- `mailapp/`: Core Django app containing models, views, and forms.
    - `models.py`: Defines `CustomUser` and `Email` models.
    - `views.py`: Handles web request logic (inbox, compose, etc.).
    - `mail_utils.py`: Helper functions for PGP encryption/decryption.
- `postguard/`: Project configuration settings.
- `templates/`: HTML templates for the web interface.
- `static/`: CSS and static assets.
- `mailserver.py`: Standalone CLI script for local mail management.
- `manage.py`: Django's command-line utility.


