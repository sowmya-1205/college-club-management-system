Project: NIT Andhra Pradesh College Club Management System

Quickstart

1. Create a virtualenv and install dependencies:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Configure environment (SQLite by default):
   cp .env.example .env

3. Run migrations and start the server:
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver 0.0.0.0:8000

4. Login at /admin/ to manage data. Public site at /.

Database

- Default is SQLite for local demo (set USE_SQLITE=1 in .env)
- For PostgreSQL, set POSTGRES_* env vars and USE_SQLITE=0

Media and Static

- Place college logo/placeholders in static/pics/
- Uploads stored under media/

Notes

- Custom user model: clubs1.CustomUser
- App URLs mounted at root via config/urls.py
