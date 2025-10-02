from django import forms
from .models import CustomUser, CustomUserManager
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator


class ContactUsForm(forms.Form):
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

    name = forms.CharField(label="Name", max_length=150)
    email = forms.EmailField(label="Your Email")
    subject = forms.CharField(max_length=255, label="Subject")
    message = forms.CharField(widget=forms.Textarea, label="Message")
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        label="Department",
        required=True
    )

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username or email'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Remove 'request' from kwargs
        super().__init__(*args, **kwargs)  # Call the base class constructor

    def clean_username(self):
        username_or_email = self.cleaned_data['username']
        CustomUser = get_user_model()  # Use the custom user model

        if '@' in username_or_email:  # It's an email address
            try:
                # Attempt to find the user by email
                user = CustomUser.objects.get(email=username_or_email)
                return user.username  # Return the username for authentication
            except CustomUser.DoesNotExist:
                raise ValidationError('No account found with this email address.')
        else:
            # Assume it's a username
            return username_or_email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("Password cannot be empty")
        return password

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # Check if the username/email and password match
        if username_or_email and password:
            CustomUser = get_user_model()  # Use the custom user model
            try:
                if '@' in username_or_email:
                    user = CustomUser.objects.get(email=username_or_email)
                else:
                    user = CustomUser.objects.get(username=username_or_email)
                if not user.check_password(password):
                    raise ValidationError("Incorrect password.")
            except CustomUser.DoesNotExist:
                raise ValidationError("Invalid username or email.")
        return cleaned_data

    
class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )
    phone_number = forms.CharField(
        max_length=15,
        validators=[MinLengthValidator(11)],
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )
    name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )
    surname = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'name', 'surname', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Create a password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, fields in self.fields.items():
            fields.widget.attrs.update({'placeholder': field_name})

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already taken.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.first_name = self.cleaned_data['name']
        user.last_name = self.cleaned_data['surname']
        if commit:
            user.save()
        return user
    
from django import forms
from .models import Appointment, Specialist
from datetime import timedelta, datetime
from django.core.exceptions import ValidationError

class AppointmentForm(forms.ModelForm):
    DURATION_CHOICES = [
        (30, '30 mins'),
        (45, '45 mins'),
        (60, '1 hour'),
        (120, '2 hours'),
        (180, '3 hours'),
    ]

    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Appointment Length")

    class Meta:
        model = Appointment
        fields = ['specialist', 'date', 'time', 'duration']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure correct input formats
        self.fields['date'].input_formats = ['%Y-%m-%d']
        self.fields['time'].input_formats = ['%H:%M']

        # Disable the specialist field when editing an existing appointment
        if self.instance and self.instance.pk:
            self.fields['specialist'].widget.attrs['disabled'] = 'disabled'

    def clean_duration(self):
        """Convert duration to timedelta object"""
        duration = self.cleaned_data.get('duration')

        # Debugging line to check the value of duration before conversion
        print(f"DEBUG: Duration selected: {duration}")

        try:
            # Convert the selected duration to timedelta in minutes
            duration = int(duration)
            duration_timedelta = timedelta(minutes=duration)
        except ValueError:
            raise forms.ValidationError("Invalid duration value.")

        # Debugging line to check the timedelta value after conversion
        print(f"DEBUG: Duration as timedelta: {duration_timedelta}")

        return duration_timedelta  # Return as timedelta

    def clean(self):
        """Custom validation to check availability and overlapping appointments"""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        duration = cleaned_data.get('duration')
        specialist = cleaned_data.get('specialist')

        if date and time and duration and specialist:
            # Convert time if necessary (ensuring it's a time object)
            if isinstance(time, datetime):
                time = time.time()

            # Combine date and time to form a datetime object
            start_datetime = datetime.combine(date, time)
            end_datetime = start_datetime + duration  # Use timedelta here

            # Compare against specialist's availability
            availability_start = datetime.combine(date, specialist.availability_start)
            availability_end = datetime.combine(date, specialist.availability_end)

            if start_datetime < availability_start or end_datetime > availability_end:
                raise forms.ValidationError(
                    f"Appointment must be within the specialist's available hours: "
                    f"{specialist.availability_start} to {specialist.availability_end}."
                )

            # Check for overlapping appointments
            overlapping_appointments = Appointment.objects.filter(
                specialist=specialist,
                date=date
            ).exclude(id=self.instance.id)  # Exclude current appointment for editing

            for appointment in overlapping_appointments:
                appointment_start = datetime.combine(appointment.date, appointment.time)
                appointment_end = appointment_start + appointment.duration  # Compare using timedelta

                # Check for overlap
                if start_datetime < appointment_end and end_datetime > appointment_start:
                    raise forms.ValidationError("This time slot is already booked.")

        return cleaned_data


from django.contrib.auth import get_user_model
from django.conf import settings

class SpecialistForm(forms.ModelForm):
    class Meta:
        model = Specialist
        fields = ['user', 'name', 'specialty', 'email', 'phone_number', 'availability_start', 'availability_end', 'is_active']
        widgets = {
            'availability_start': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'availability_end': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the 'user' field to only users who are not already assigned as specialists
        User = get_user_model()  # Get the user model dynamically
        self.fields['user'].queryset = User.objects.filter(specialist__isnull=True)  # Filter users who are not specialists

        # Add the specialty choices dropdown (optional but included here for clarity)
        self.fields['specialty'].choices = Specialist.SPECIALTY_CHOICES
        
from django import forms
from django.contrib.auth.forms import SetPasswordForm

class PasswordResetForm(SetPasswordForm):
    """Custom password reset form to handle password reset logic."""
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password1")
        confirm_password = cleaned_data.get("new_password2")
        
        if password != confirm_password:
            raise forms.ValidationError("The two password fields must match.")
        
        return cleaned_data


