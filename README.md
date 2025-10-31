# Privacy-by-Design Home Services (Django)

A secure “Home Services” demo app for **COMP SCI 7412/4812 – Secure Software Engineering**.  
It demonstrates **privacy-by-design**: minimal data collection, TOTP 2FA, secure cookies, brute‑force protection (django‑axes), CSRF, and basic authorization for sensitive operations..

Group Members:
- Aditya Dixit
- Atiq Ullah Ador
- Chirag Giri
- Sk Md Shariful Islam Arafat
- Vishal Shrikanth Kulkarni
- Khush Patel

---

## 1. Install the Environment

### Prerequisites
- Python **3.11+** (works on 3.12/3.14)
- `pip` and `venv`
- (Optional) PostgreSQL 14+ (SQLite used by default)

### Clone & Create Virtualenv
```bash
git clone <YOUR-REPO-URL> home-services
cd home-services

python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows PowerShell
# .\venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> If a migration hook tries to run `black` and you don't have it, either install it (`pip install black`) or disable that hook.

### Configure Environment
Create a **.env** in the project root (values for development; change for production):
```env
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost

# SQLite by default (no DB URL needed)
# To use Postgres, uncomment and edit:
# DATABASE_URL=postgres://user:pass@127.0.0.1:5432/homeservices

# Cookies (turn these True in production w/ HTTPS)
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Axes (brute-force protection)
AXES_ENABLED=True
AXES_COOLOFF_TIME=1  # hours
```

### Database Migrations & Superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Run the Dev Server
```bash
python manage.py runserver
```
Open: **http://127.0.0.1:8000**

---

## 2. Commands

Fresh start
```bash
python manage.py flush # deletes all rows from all tables (asks for "yes")
python manage.py clearsessions # removes expired sessions
python manage.py axes_reset # clears django-axes lockouts (if used)
Remove-Item -Recurse -Force .\media\* # remove uploaded files (vaccination proofs, etc.)

```

```bash
# Start server
python manage.py runserver

# Make & apply migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static (production)
python manage.py collectstatic

# Check for issues
python manage.py check

# Freeze requirements
pip freeze > requirements.txt
```

### django-axes Utilities (brute-force defense)
```bash
# Reset ALL lockouts (useful during dev)
python manage.py axes_reset

# Reset a single user
python manage.py axes_reset_username <username>

# Reset by IP
python manage.py axes_reset_ip 127.0.0.1
```
---

## 3. Role-based Access Control
Only staff administrators can create or edit Services and Packages. Admin portal: http://127.0.0.1:8000/admin/. Sign in with the superuser to manage:

- Catalog → Services
- Catalog → Service packages

Regular users cannot access the admin portal and cannot create or modify services and packages.

## 4. Two‑Factor Authentication (TOTP)

**Enable**
1. Log in → **Profile** (`/profile/`).
2. In the 2FA card, scan the QR or copy the secret into your authenticator app.
3. Enter the 6‑digit code → **Verify & Enable**.

**Login flow with 2FA**
- Enter username/password and submit.
- If required, an **OTP modal** opens → enter code → sign in.

## 5. Encryption and Secure Defaults

- Passwords are hashed by Django’s authentication subsystem.
- CSRF protection is enabled by default.

## 6. Vaccination Proof at Registration
- Go to Register: http://127.0.0.1:8000/accounts/register/
- Complete the form and upload a PDF vaccination certificate (max 2 MB).
- After registration, the file is stored on the server and visible on the Profile page. It is flagged as: Not provided, awaiting verfication, or verified.
- Staff can review and set the verified flag in the admin for the corresponding user profile.
- Files are stored under MEDIA_ROOT/vaccination/ and served from /media/ during development.

## 7. Contact Tracing and Anonymous Exposure Alerts
- The app supports basic anonymous contact alerts tied to bookings.
- Once a worker goes to the bookings page, opens a booking and clicks check-in, it logs contact.
- To report a positive test anonymously, go to Profile -> Health -> Report Positive COVID. The system finds recent contact logs and creates anonymous alerts for those users.
- Affected users see a red Exposure Warning banner until they dismiss it or it expires. No identity is disclosed to recipients of exposure alerts.

## 8. Payment System and Invoices
- The app provides a demo payment flow and generates invoices for bookings.
- Step 1: As an admin, create a Service or Package with a non-zero price in the admin portal.
- Step 2: As a user, create a New Booking and select that Service or Package.
- Step 3: Open the booking detail page. If a quoted_price_cents exists, a Pay now button is shown.
- Step 4: Click Pay now to simulate a successful payment.
- Step 5: After payment, an Invoice is created and listed at the bottom of the booking detail page. You can click the invoice number to view the invoice detail.
- If no quoted_price_cents exists, the Pay now button is hidden.

## 9. Delete Account
- Users can delete their own accounts from the app. The deletion flow removes the user account and scrubs related personal profile data where appropriate.
- Go to Profile and use the Delete account action.
- Enter your password (and OTP if set-up) to confirm the action.

## 10. Data Retention: 15-Day Privacy Window
- Sensitive records such as exposure alerts are intended to expire after approximately 15 days. 
- To simulate, follow the instructions in expire_15days_script.py.

## 11. Troubleshooting

- **405 on /logout**: Ensure you submit a **POST** form to `users:logout` and use Django’s `LogoutView`.
- **TemplateDoesNotExist: users/locked_out.html**: Add `templates/users/locked_out.html` or set `AXES_LOCKOUT_URL` to a custom view.
- **Axes username callable error**: If you override `AXES_USERNAME_CALLABLE`, it must accept `(request, credentials)`; otherwise remove it.
- **OTP modal doesn’t appear**: Ensure Bootstrap bundle is loaded (without `defer`) or the inline script waits for `window.bootstrap`.
- **Black not found**: `pip install black` or disable the migration formatter hook.

## 12. Project Layout (selected)

```
core/         – settings, urls, base views/templates
users/        – Login/Register, custom 2FA login form (modal flow)
profiles/     – UserProfile, profile detail + embedded 2FA panel
catalog/      – Services & Packages list/detail
bookings/     – Booking models, list/detail, status transitions
payments/     – (stub) payment examples
templates/    – base.html and app templates
static/       – favicon & assets
```
