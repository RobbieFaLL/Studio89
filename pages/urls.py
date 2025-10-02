from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (Home, AboutUs, contactus, 
                    signup, custom_login_view, 
                    check_user_exists, check_user_exists_password, 
                    Tatooist, Barber, Therapist,
                    Hairdresser, Nailtech,
                    DogGroomer, Physiotherapist,
                    Chiropractor, Booking, Dashboard, 
                    Payment, appointment_success,
                    PaymentFailed, AddSpecialist, 
                    get_user_data, cancel_appointment,
                    view_appointments, amend_appointment, 
                    password_reset_request, password_reset_verify, 
                    password_reset_confirm)

urlpatterns = [
    # Home and Static Pages
    path('', Home, name='Home'),
    path('AboutUs', AboutUs, name='About'),
    path('ContactUs', contactus, name='Contact'),
    
    # Specialist Pages
    path('Tatooist', Tatooist, name="Tatoo"),
    path("Barber", Barber , name="Barber"),
    path("Therapist", Therapist, name="Therapist"),
    path("Hairdresser",Hairdresser, name="Hairdresser"),
    path("NailTech",Nailtech, name="NailTech"),
    path("DogGroomer",DogGroomer, name="DogGroomer"),
    path("Chiropractor",Chiropractor, name="Chiropractor"),
    path("Physiotherapist",Physiotherapist, name="Physiotherapist"),
    
    # Authentication Routes
    path('signup/', signup, name='signup'),
    path('login/', custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    
    # Booking and Dashboard
    path("Booking", Booking, name="Booking"),
    path("Dashboard", Dashboard, name="Dashboard"),
    
    # Specialist Management
    path('add-specialist/', AddSpecialist, name='add_specialist'),
    
    # Payment Routes
    path("Payment/<int:booking_id>/", Payment, name="Payment"),
    path("Payment/success", appointment_success, name="Success"),
    path("Payment/Failed/<int:appointment_id>/", PaymentFailed, name="Failed"),
    
    # Appointment Management Routes
    path('cancel_appointment/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    
    # View and Amend Appointments
    path('specialist/<int:specialist_id>/appointments/', view_appointments, name='view_appointments'),
    path('appointment/<int:appointment_id>/amend/', amend_appointment, name='amend_appointment'),
    
    # User Validation Routes
    path('get_user_data/<int:user_id>/', get_user_data, name='get_user_data'),
    path('check_user_exists/', check_user_exists, name='check_user_exists'),
    path('check_user_exists_password/', check_user_exists_password, name='check_user_exists_password'),

    # Password Reset Routes (Custom views)
    path('password_reset/', password_reset_request, name='password_reset_request'),
    path('password_reset/verify/', password_reset_verify, name='password_reset_verify'),
    
    # Custom Password Reset Confirmation (Override built-in view)
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    
    # Built-in Password Reset Views
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
