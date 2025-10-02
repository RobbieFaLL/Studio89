# Installation Guide

This guide will walk you through setting up the Studio89 Django project on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (recommended: Python 3.11 or newer)
- **Git**
- **pip** (Python package installer)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RobbieFaLL/Studio89.git
cd Studio89
```

### 2. Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

**On Windows:**
```cmd
python -m venv env
env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Generate a Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edit the `.env` file and:
- Replace `your_secret_key_here` with the generated secret key
- Configure other settings as needed (see Configuration section below)

### 5. Set Up the Database

```bash
# Run migrations to create database tables
python manage.py migrate

# (Optional) Create a superuser account
python manage.py createsuperuser
```

### 6. Collect Static Files (Production)

```bash
python manage.py collectstatic
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see your application running!

## Configuration

### Database Configuration

**SQLite (Default - Development):**
```env
DATABASE_URL=
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### Email Configuration (Mailgun)

1. Sign up at [Mailgun](https://www.mailgun.com/)
2. Get your API key and domain
3. Update your `.env` file:

```env
MAILGUN_API_KEY=your_api_key_here
MAILGUN_DOMAIN_NAME=your_domain_here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Payment Configuration (Stripe)

1. Sign up at [Stripe](https://stripe.com/)
2. Get your test API keys
3. Add to your Django settings (follow Stripe documentation)

## Troubleshooting

### Common Issues

**Import Error: No module named 'django'**
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt`

**Database Issues**
- Delete `db.sqlite3` and run `python manage.py migrate` again
- Check your `DATABASE_URL` configuration

**Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check your `STATIC_URL` and `STATICFILES_DIRS` settings

**Permission Denied**
- Make sure you have write permissions in the project directory
- On Unix systems, you might need to use `sudo` for certain operations

### Getting Help

- Check the existing [Issues](https://github.com/RobbieFaLL/Studio89/issues)
- Read the [Contributing Guidelines](CONTRIBUTING.md)
- Open a new issue if you need help

## Next Steps

After installation:

1. Explore the admin interface at `/admin/`
2. Check out the main application features
3. Read the code to understand the Django patterns used
4. Try making modifications to learn more

## Development Tools

Consider installing these tools for better development experience:

- **Django Debug Toolbar**: `pip install django-debug-toolbar`
- **Django Extensions**: `pip install django-extensions`
- **Code formatting**: `pip install black isort`