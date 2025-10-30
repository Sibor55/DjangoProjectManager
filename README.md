# Django Project Manager

A Django-based project management app for teams and tasks.

## stack
- Django 5.2.7
- PostgreSQL
- Environment variables with python-decouple

## Quick Start
1. Clone repo & create virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with database credentials
4. Run: `python manage.py migrate`
5. Start: `python manage.py runserver`

## Setup .env
```ini
SECRET_KEY=your-secret-key
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_pass
DB_HOST=localhost
DB_PORT=5432
```

Visit `http://localhost:8000`

**Under Development** - Core features working, task views in progress.
