# Security Policy

## Overview
This document outlines the security practices and recommendations for the Studio89 Django project. It is intended to help contributors and users maintain a secure deployment and development environment.

---

## 1. Secrets & Sensitive Data
- All secrets (SECRET_KEY, API keys, credentials) must be stored in the `.env` file and never hardcoded in code or templates.
- Never commit `.env` or any file containing secrets to version control. `.env` is excluded via `.gitignore`.

## 2. Environment Files
- Use `.env.example` to share required environment variables without exposing secrets.
- Always update `.env.example` when new environment variables are added.

## 3. Django Settings
- `DEBUG` must be set to `False` in production.
- `ALLOWED_HOSTS` must be set to your domain(s) in production.
- Use strong, unique values for `SECRET_KEY`.
- Password validation is enabled by default.

## 4. Database
- Default is SQLite for local development. Use PostgreSQL or another secure database for production.
- Database credentials must be stored in `.env`.

## 5. Email & Third-Party Services
- Email backend credentials (Mailgun, etc.) are loaded from `.env`.
- Stripe and other payment keys are loaded from `.env`.
- Never expose private API keys in templates or client-side code.

## 6. Static & Media Files
- Do not store sensitive files in static or media directories.
- Ensure proper permissions on uploaded files.

## 7. Authentication & Authorization
- Custom user model is used for flexibility.
- CSRF protection is enabled by default.
- All sensitive views require authentication.

## 8. Dependency Management
- Use `requirements.txt` for dependencies.
- Keep dependencies up to date and monitor for vulnerabilities.

## 9. Git & Repository Hygiene
- `.gitignore` excludes all sensitive/system files, environment folders, and database files.
- Remove any unwanted files before public release.

## 10. Reporting Vulnerabilities
If you discover a security vulnerability, please open an issue or contact the repository owner directly. Do not disclose vulnerabilities publicly until they are resolved.

---

## References
- [Django Security Checklist](https://docs.djangoproject.com/en/5.1/topics/security/)
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)

---

**Maintainers should review this policy regularly and update as needed.**
