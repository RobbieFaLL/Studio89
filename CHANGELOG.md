# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Environment variable configuration with .env support
- Comprehensive .gitignore for Django projects
- .env.example template for easy setup

### Changed
- Improved security by moving sensitive settings to environment variables

### Fixed
- Database configuration now properly handles both SQLite and PostgreSQL

## [1.0.0] - 2024-XX-XX

### Added
- Initial release of Studio89 booking platform
- User registration and authentication system
- Appointment booking, amendment, and cancellation
- Specialist and staff dashboard functionality
- Email notifications via Mailgun
- Payment integration with Stripe (test mode)
- Custom user model implementation
- Bootstrap 5 responsive design
- Support for multiple service types (tattoo, beauty, barber, etc.)

### Features
- Multi-service booking platform
- User account management
- Staff appointment management
- Email notification system
- Payment processing
- Mobile-responsive interface

### Technical
- Django web framework
- SQLite database (development)
- Bootstrap frontend
- Mailgun email service
- Stripe payment integration