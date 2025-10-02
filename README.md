# Studio89 Django Project


**Note:** This project was built as a college project in 2024, before the official Studio 89 website ([studio89bournemouth.co.uk](https://www.studio89bournemouth.co.uk/)) was released. It is not affiliated with the official business or website.

## Project Overview
Studio89 is a Django-based web application designed as a self-care space booking platform. It allows users to book appointments with tattooists, beauticians, barbers, hair stylists, dog groomers, and more. This project was created for educational purposes and demonstrates a full-stack approach to building a multi-service booking system.

## Features
- User registration and authentication
- Book, amend, and cancel appointments
- Specialist and staff dashboards
- Email notifications for bookings and password resets
- Payment integration (Stripe)
- Custom user model
- Responsive design using Bootstrap

## Technology Stack
- Python 3
- Django
- SQLite (default, easily swappable)
- Bootstrap 5
- Stripe API (test mode)
- Mailgun (for email)

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd Studio89
   ```

2. **Create your environment file:**
   Copy the example file and fill in your secrets:
   ```sh
   cp .env.example .env
   # Edit .env and set your SECRET_KEY, database, and email settings
   ```

3. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv env
   source env/bin/activate
   ```

4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

5. **Run migrations:**
   ```sh
   python manage.py migrate
   ```

6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## Security Notes
- Never commit your `.env` file or any secrets to GitHub.
- Always use environment variables for sensitive settings.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is released for educational purposes only. If you wish to use or modify it for commercial use, please check with the original author and ensure you comply with all relevant laws and third-party service terms.
