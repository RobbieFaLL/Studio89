from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.template.loader import render_to_string
from .forms import ContactUsForm, CustomLoginForm, CustomSignupForm, SpecialistForm
from .models import ContactUs, CustomUser
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.mail import send_mail, get_connection
from django.utils.html import strip_tags
import requests
from django.contrib.auth import get_user_model
from Studio89.settings import DEFAULT_FROM_EMAIL, MAILGUN_API_KEY, EMAIL_BACKEND, MAILGUN_DOMAIN_NAME
from django.http import HttpResponseForbidden

connection = get_connection(
    EMAIL_BACKEND,
    api_key=MAILGUN_API_KEY,
    domain=MAILGUN_DOMAIN_NAME,
    fail_silently=False
)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def Home(request):
    return render (request, 'home/index.html')

def AboutUs(request):
    return render (request, 'home/about.html')


def contactus(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            # Get values from form
            name = form.cleaned_data["name"]
            subject = form.cleaned_data["subject"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            department = form.cleaned_data["department"]
            from_email = DEFAULT_FROM_EMAIL

            # Render email template with context
            email_context = {'name': name}
            email_template = render_to_string('contact/contact.html', email_context)

            # Send email
            send_mail(
                subject,
                message,
                DEFAULT_FROM_EMAIL,
                ['robertfall98@gmail.com'],
                connection=connection,
                html_message=email_template
            )

            # Create and save contact
            contact = ContactUs(
                name=name,
                subject=subject,
                email=email,
                message=message,
                department=department,
                ip_address=get_client_ip(request)  # Store client IP for reference
            )
            contact.save()

            messages.success(request, "Thanks for contacting us!")
            return redirect("/")
    else:
        form = ContactUsForm()

    context = {'form': form}
    return render(request, "contact/contactus.html", context)

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create user instance but don't save yet
            user.save()  # Now save it properly

            # Explicitly set the authentication backend
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Adjust if using a custom backend

            login(request, user)  # Log in the user

            # Debugging: Check if the email exists
            print(f"User email: {user.email}")  # Should print the actual email

            # Email setup
            context = {'user': user}
            email_html = render_to_string('accounts/account_confirmation.html', context)
            email_plain = strip_tags(email_html)

            # Mailgun API setup
            mailgun_url = f"https://api.mailgun.net/v4/{MAILGUN_DOMAIN_NAME}/messages"
            mailgun_auth = ("api", MAILGUN_API_KEY)
            mailgun_data = {
                "from": DEFAULT_FROM_EMAIL,
                "to": user.email,
                "subject": "Welcome to Studio 89!",
                "text": email_plain,
                "html": email_html
            }

            # Send email via Mailgun API
            try:
                response = requests.post(mailgun_url, auth=mailgun_auth, data=mailgun_data, verify=False)
                
                if response.status_code == 200:
                    messages.success(request, "Account created successfully! Please check your email for confirmation.")
                else:
                    messages.warning(request, "Account created, but there was an issue sending the confirmation email.")
            except requests.exceptions.RequestException as e:
                messages.warning(request, f"Your account was created, but we couldn't send a confirmation email: {str(e)}")

            return redirect('Home')  # Always redirect to Home after form submission

        else:
            # Handle form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

    else:
        form = CustomSignupForm()

    return render(request, 'accounts/signup.html', {'form': form})

# Custom Login View
def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            CustomUser = get_user_model()

            try:
                user = CustomUser.objects.get(email=username_or_email) if '@' in username_or_email else CustomUser.objects.get(username=username_or_email)
            except CustomUser.DoesNotExist:
                form.add_error('username', 'User not found.')
                return render(request, 'login.html', {'form': form})

            if user.check_password(password):
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return redirect('Dashboard')
            else:
                form.add_error(None, 'Invalid password.')

    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return render(request, 'accounts/logout.html')

def check_user_exists(request):
    username_or_email = request.GET.get('username_or_email')
    exists = CustomUser.objects.filter(email=username_or_email).exists() if '@' in username_or_email else CustomUser.objects.filter(username=username_or_email).exists()
    return JsonResponse({'exists': exists})

# Check if User Exists with Password (AJAX)
def check_user_exists_password(request):
    username_or_email = request.GET.get('username_or_email')
    password = request.GET.get('password')

    if not username_or_email or not password:
        return JsonResponse({"valid": False, "error_type": "missing_fields"})

    CustomUser = get_user_model()

    try:
        user = CustomUser.objects.get(email=username_or_email) if '@' in username_or_email else CustomUser.objects.get(username=username_or_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({"valid": False, "error_type": "user_not_found"})

    user = authenticate(request, username=user.username, password=password)

    return JsonResponse({"valid": True} if user else {"valid": False, "error_type": "invalid_password"})

def Tatooist(request):
    return render(request, 'outlets/Tatooist.html')

def Barber(request):
    return render(request, 'outlets/barber.html')

def Therapist(request):
    return render(request, 'outlets/therapist.html')

def Hairdresser(request):
    return render(request, 'outlets/hairdresser.html')

def Nailtech(request):
    return render(request, 'outlets/nailtech.html')

def DogGroomer(request):
    return render(request, 'outlets/doggroomer.html')

def Physiotherapist(request):
    return render(request, 'outlets/physiotherapist.html')

def Chiropractor(request):
    return render(request, 'outlets/chiropractor.html')

def send_appointment_email(user, subject, context, template_html, template_plain):
    email_html = render_to_string(template_html, context)
    email_plain = strip_tags(email_html)
    from_email = DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        email_plain,  # Plain-text email content
        DEFAULT_FROM_EMAIL,
        [user.email],  # Send to the correct user
        connection=connection,
        html_message=email_html
    )


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Specialist, Appointment
from .forms import AppointmentForm
from datetime import datetime, time

import stripe
from django.conf import settings

stripe.api_key = your_stripe_secret_key = settings.STRIPE_SECRET_KEY

import logging

from datetime import timedelta, datetime
from django.core.exceptions import ValidationError

# Initialize logger
logger = logging.getLogger(__name__)

@login_required
def Booking(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user  # Assign logged-in user
            appointment.status = 'PENDING'  # Default status

            try:
                appointment.save()  # Triggers `clean()`
                return redirect('Payment', booking_id=appointment.id)
            except ValidationError as e:
                form.add_error(None, e.messages[0])  # Show validation errors in form
            except Exception as e:
                form.add_error(None, f"Error saving appointment: {e}")

    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {'form': form})


import logging

logger = logging.getLogger(__name__)

@login_required
def Payment(request, booking_id):
    appointment = get_object_or_404(Appointment, id=booking_id, user=request.user)
    amount_in_pence = int(appointment.total_price * 100)  # Calculate amount in pence
    logger.debug(f"Appointment total price: {appointment.total_price}")  # Debugging line
    if request.method == 'POST':
        try:
            charge = stripe.Charge.create(
                amount=amount_in_pence,  # Use the calculated amount in pence
                currency="gbp",
                description=f"Appointment with {appointment.specialist.name} on {appointment.date} at {appointment.time}",
                source=request.POST['stripeToken']
            )
            appointment.payment_status = "PAID"
            appointment.status = "CONFIRMED"
            appointment.save()
            return redirect('appointment_success')
        except stripe.error.CardError as e:
            logger.error(f"Card error: {e}")
            return redirect('Failed', appointment_id=appointment.id)
        except stripe.error.RateLimitError as e:
            logger.error(f"Rate limit error: {e}")
            return redirect('Failed', appointment_id=appointment.id)
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid request error: {e}")
            return redirect('Failed', appointment_id=appointment.id)
        except stripe.error.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return redirect('Failed', appointment_id=appointment.id)
        except stripe.error.APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            return redirect('Failed', appointment_id=appointment.id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return redirect('Failed', appointment_id=appointment.id)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return redirect('Failed', appointment_id=appointment.id)
    else:
        return render(request, 'payments/payment.html', {'appointment': appointment, 'amount_in_pence': amount_in_pence})

@login_required
def appointment_success(request):
    return render(request, 'appointments/appointment_success.html')

@login_required
def PaymentFailed(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    return render(request, 'payments/paymentfailed.html', {'appointment': appointment})

@login_required
def Dashboard(request):
    if request.user.is_staff:
        # Fetch all specialists for staff members
        specialists = Specialist.objects.all()

        # Assuming the user has a profile with a 'specialty' field
        user_specialty = request.user.profile.specialty  # Adjust based on your model

        # Define the specialties to filter on
        specialties = [
            'Beauticians', 'hairdresser', 'tattoo_artist', 'nail_technician',
            'dog_groomer', 'aesthetic_practitioner', 'sports_therapist', 
            'physiotherapist', 'chiropractor', 'semi_permanent_makeup'
        ]

        # If the user is a specialist, show appointments for that specialty
        if user_specialty in specialties:
            appointments = Appointment.objects.filter(specialist__specialty=user_specialty)
            client_appointments = Appointment.objects.filter(user=request.user)
        else:
            # If user is staff but not a specialist, show all appointments for this staff member
            appointments = Appointment.objects.filter(specialist__user=request.user)
            client_appointments = Appointment.objects.filter(user=request.user)
        
            return render(request, 'appointments/staff_dashboard.html', {
            'specialists': specialists,
            'appointments': appointments,
            'client_appointments': client_appointments})

    else:
        # For regular users (clients), show their own appointments
        client_appointments = Appointment.objects.filter(user=request.user)

        # Render the user dashboard with the client appointments
        return render(request, 'appointments/user_dashboard.html', {'client_appointments': client_appointments})

@login_required
def AddSpecialist(request):
    if request.method == 'POST':
        form = SpecialistForm(request.POST)
        if form.is_valid():
            # Assign the currently logged-in user (or any other user instance)
            user = request.user  # You can also use User.objects.get(id=some_id) to get another user
            specialist = form.save(commit=False)
            specialist.user = user
            specialist.save()
            return redirect('Dashboard')  # Redirect to the specialist list or another page
    else:
        form = SpecialistForm()
    return render(request, 'appointments/add_specialist.html', {'form': form})

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()  # Save the appointment
            return redirect('appointment_success')  # Redirect to success page
    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {'form': form})

def get_user_data(request, user_id):
    try:
        # Fetch the user using the provided ID
        user = get_user_model().objects.get(id=user_id)
        
        # Prepare the response with the relevant data
        data = {
            'name': user.get_full_name(),  # Or user.name if that's how you store it
            'email': user.email,
            'phone_number': user.phone_number,  # Directly from the user model
        }
        
        # Return the data as JSON
        return JsonResponse(data)
    except get_user_model().DoesNotExist:
        # Return error if user not found
        return JsonResponse({'error': 'User not found'}, status=404)
    
from django.http import HttpResponseRedirect
from django.urls import reverse
@login_required
def view_appointments(request, specialist_id):
    specialist = get_object_or_404(Specialist, id=specialist_id)
    appointments = Appointment.objects.filter(specialist=specialist)

    return render(request, 'appointments/specialist_appointments.html', {'specialist': specialist, 'appointments': appointments})

# Amend an appointment's details (time, etc.)
@login_required
def amend_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)  # Load form with submitted data
        if form.is_valid():
            form.save()  # Save the changes to the database

            # Determine the recipient of the email
            if request.user == appointment.user:
                recipient = appointment.specialist.user  # Notify the specialist
                subject = "An Appointment Has Been Amended by Your Client"
            else:
                recipient = appointment.user  # Notify the client
                subject = "Your Appointment Time Has Been Amended"

            # Send email notification
            context = {'user': recipient, 'appointment': appointment}
            recipient_email = getattr(recipient, 'email', None)
            if recipient_email:
                send_appointment_email(
                    user=recipient,
                    subject=subject,
                    context=context,
                    template_html="appointments/appointment_amended.html",
                    template_plain="appointments/appointment_amended.txt"
                )


            return redirect('Dashboard')  # Redirect to Dashboard after saving
    else:
        form = AppointmentForm(instance=appointment)  # Pre-fill form with existing data

    return render(request, 'appointments/amend_appointment.html', {
        'form': form,
        'appointment': appointment  # Used for cancel links
    })

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Cancel the appointment
    appointment.status = "Cancelled"
    appointment.save()

    # Send email notification to the user
    context = {'user': appointment.user, 'appointment': appointment}
    recipient_email = getattr(appointment.user, 'email', None)
    if recipient_email:
        send_appointment_email(
            user=appointment.user,
            subject="Your Appointment Has Been Cancelled",
            context=context,
            template_html="appointments/appointment_cancelled.html",
            template_plain="appointments/appointment_cancelled.txt"
        )


    return redirect('Dashboard')

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.conf import settings
from .models import UserProfile
from .forms import SetPasswordForm
from django.http import Http404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = get_user_model().objects.get(email=email)

            # Generate reset token
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.generate_reset_token()

            # Render email template with context
            email_context = {'user': user, 'reset_token': profile.reset_token}
            email_template = render_to_string('accounts/password_reset_email.html', email_context)
            email_plain = strip_tags(email_template)
            from_email = DEFAULT_FROM_EMAIL  # Ensure this is set in your settings

            # Ensure the subject is a clean string
            subject = "Password Reset Request"

            send_mail(
                'password reset request',  # Subject
                email_plain,  # Plain-text version of the email
                from_email,  # Sender email (must match your Mailgun settings)
                [user.email],  # Recipient list (must be a list)
                html_message=email_template,  # HTML version of the email
                connection=connection
            )

            messages.success(request, "A password reset token has been sent to your email.")
            return redirect('password_reset_verify')

        except get_user_model().DoesNotExist:
            messages.error(request, "Email address not found.")

    return render(request, 'accounts/password_reset_request.html')

def password_reset_verify(request):
    if request.method == 'POST':
        token = request.POST.get('token')  # Assuming the user inputs the token here
        if token:
            try:
                # Find the user profile using the token
                profile = UserProfile.objects.get(reset_token=token)
                
                if profile.is_reset_token_valid():
                    # Create the uidb64 from user ID (convert user ID to string before encoding)
                    uidb64 = urlsafe_base64_encode(str(profile.user.pk).encode())

                    # Use the reset token
                    token = profile.reset_token
                    
                    # Redirect to the password reset confirmation page with parameters
                    return redirect('password_reset_confirm', uidb64=uidb64, token=token)
                else:
                    messages.error(request, "The reset token is invalid or has expired.")
            except UserProfile.DoesNotExist:
                messages.error(request, "Invalid token.")
        else:
            messages.error(request, "No token provided.")
    
    return render(request, 'accounts/password_reset_verify.html')

from .forms import PasswordResetForm
        
def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the uidb64 and get the user
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = get_user_model().objects.get(pk=uid)

        # Check if the token is valid for this user
        profile = UserProfile.objects.get(user=user)
        if not profile.is_reset_token_valid() or profile.reset_token != token:
            messages.error(request, "The reset token is invalid or has expired.")
            return redirect('password_reset_request')  # Redirect to the reset request page

        # If the token is valid, proceed with the password reset
        if request.method == 'POST':
            form = PasswordResetForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('login')  # Redirect to the login page after successful password reset
        else:
            form = PasswordResetForm(user=user)
    except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        messages.error(request, "Invalid token or user.")
        return redirect('password_reset_request')

    return render(request, 'accounts/password_reset_confirm.html', {'form': form})