from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User

class ContactUs(models.Model):
    DEPARTMENT_CHOICES = [
        ('Beauticians', 'Beauticians'),
        ('Hairdressers', 'Hairdressers'),
        ('Nail Technicians', 'Nail Technicians'),
        ('barbers', 'Barbers'),
        ('Tattoo Artists', 'Tattoo Artists'),
        ('Dog Groomers', 'Dog Groomers'),
        ('Aesthetic Practitioners', 'Aesthetic Practitioners'),
        ('Sports Therapists', 'Sports Therapists'),
        ('Physiotherapists', 'Physiotherapists'),
        ('Chiropractors', 'Chiropractors'),
        ('Semi-Permanent Makeup Artists', 'Semi-Permanent Makeup Artists'),
        ('other', 'Other'),
    ]
    
    class Meta:
        verbose_name_plural = "Contact us"

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, default="Site Contact")
    email = models.EmailField()
    message = models.TextField(max_length=10000)
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        default='other',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Corrected field definition

    def __str__(self):
        return self.subject


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def clean(self):
        super().clean()
        if self.phone_number and len(self.phone_number) < 11:
            raise ValidationError({"phone_number": "Phone number must be at least 11 characters long."})

    def create_profile(self):
        """Automatically create a user profile when a new user is created."""
        profile, created = UserProfile.objects.get_or_create(user=self)
        return profile

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Room(models.Model):
    ROOM_TYPES = [
        ("SMALL", "Small"),
        ("MEDIUM", "Medium"),
        ("LARGE", "Large"),
    ]
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

def get_default_user():
    User = get_user_model()
    user = User.objects.first()  # Get the first user (or modify logic as needed)
    if user:
        return user.id
    return None  # Or return a default user ID if necessary

from datetime import timedelta, datetime

class Specialist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=100)
    
    SPECIALTY_CHOICES = [
        ('Beauticians', 'Beauticians'),
        ('hairdresser', 'Hairdresser'),
        ('tattoo_artist', 'Tattoo Artist'),
        ('nail_technician', 'Nail Technician'),
        ('dog_groomer', 'Dog Groomer'),
        ('aesthetic_practitioner', 'Aesthetic Practitioner'),
        ('sports_therapist', 'Sports Therapist'),
        ('physiotherapist', 'Physiotherapist'),
        ('chiropractor', 'Chiropractor'),
        ('semi_permanent_makeup', 'Semi-Permanent Makeup Artist'),
    ]
    
    specialty = models.CharField(max_length=100, choices=SPECIALTY_CHOICES)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    availability_start = models.TimeField()  # e.g., 09:00
    availability_end = models.TimeField()    # e.g., 17:00
    is_active = models.BooleanField(default=True)
    session_price = models.DecimalField(max_digits=6, decimal_places=2, default=50.00)

    def __str__(self):
        return f"{self.name} - {self.get_specialty_display()}"

class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    date = models.DateField()  # Stores the date of the appointment
    time = models.TimeField()  # Stores the time of the appointment
    duration = models.DurationField(default=timedelta(hours=1))  # Stores the duration of the appointment with a default of 1 hour
    status = models.CharField(max_length=10, choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed')])

    def __str__(self):
        return f"Appointment with {self.specialist.name} on {self.date} at {self.time}"

    @property
    def total_price(self):
        return self.specialist.session_price

    @property
    def end_time(self):
        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + self.duration
        return end_datetime.time()

    def clean(self):
        if self.time is None:
            raise ValidationError("Time field cannot be None.")

        # Convert stored duration to timedelta (if not already)
        if isinstance(self.duration, str):  
            self.duration = timedelta(minutes=int(self.duration))  

        # Calculate appointment start and end times
        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + self.duration

        # Ensure the appointment is within specialist's available hours
        availability_start = datetime.combine(self.date, self.specialist.availability_start)
        availability_end = datetime.combine(self.date, self.specialist.availability_end)

        if start_datetime < availability_start or end_datetime > availability_end:
            raise ValidationError(f"Appointment must be within the specialist's available hours: {self.specialist.availability_start} to {self.specialist.availability_end}.")

        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            specialist=self.specialist,
            date=self.date
        ).exclude(id=self.id)  # Exclude itself when editing

        for existing_appointment in overlapping_appointments:
            existing_start = datetime.combine(existing_appointment.date, existing_appointment.time)
            existing_end = existing_start + existing_appointment.duration

            # Overlapping check: new appointment should not start before an existing one ends and vice versa
            if start_datetime < existing_end and end_datetime > existing_start:
                raise ValidationError("This time slot is already booked.")

        return super().clean()
    
import random
import string
from django.utils import timezone

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    # Reset token fields
    reset_token = models.CharField(max_length=6, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)
    SPECIALTY_CHOICES = [
        ('Beauticians', 'Beauticians'),
        ('Hairdressers', 'Hairdressers'),
        ('Nail Technicians', 'Nail Technicians'),
        ('Tattoo Artists', 'Tattoo Artists'),
        ('Dog Groomers', 'Dog Groomers'),
        ('Aesthetic Practitioners', 'Aesthetic Practitioners'),
        ('Sports Therapists', 'Sports Therapists'),
        ('Physiotherapists', 'Physiotherapists'),
        ('Chiropractors', 'Chiropractors'),
        ('Semi-Permanent Makeup Artists', 'Semi-Permanent Makeup Artists'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    specialty = models.CharField(max_length=100, choices=SPECIALTY_CHOICES, blank=True, null=True) 

    def __str__(self):
        return f"Profile for {self.user.username} ({self.get_specialty_display()})"

    def generate_reset_token(self):
        """Generate a random 6-digit numeric token and ensure uniqueness."""
        self.reset_token = ''.join(random.choices(string.digits, k=6))  # Using only digits for simplicity
        self.reset_token_expiry = timezone.now() + timedelta(hours=1)  # Token expires in 1 hour
        self.save()

    def is_reset_token_valid(self):
        """Check if the reset token is still valid."""
        return self.reset_token and self.reset_token_expiry and timezone.now() < self.reset_token_expiry

    def clear_reset_token(self):
        """Clears the reset token after use."""
        self.reset_token = None
        self.reset_token_expiry = None
        self.save()