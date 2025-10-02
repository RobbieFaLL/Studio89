from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Specialist, Appointment, UserProfile

# UserProfile Inline
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False  # Prevent deletion of the profile from the inline
    verbose_name_plural = 'Profile'

# Custom User Admin with UserProfile inline
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

    # Extend the default UserAdmin fieldsets to include custom fields
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )

    # Add the UserProfileInline to the CustomUserAdmin
    inlines = [UserProfileInline]

    # Ensure a profile is created when a user is saved
    def save_model(self, request, obj, form, change):
        if not obj.profile:  # Check if the user has a profile
            obj.create_profile()  # Create the profile if it doesn't exist
        super().save_model(request, obj, form, change)


# Appointment Admin to restrict access based on logged-in user's specialty
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'date', 'time')
    search_fields = ('specialist__name', 'date', 'time')
    list_filter = ('date', 'specialist')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_authenticated:
            # Check if the user is a specialist (i.e., has a Specialist entry)
            specialist = Specialist.objects.filter(user=request.user).first()
            if specialist:
                # Only show appointments related to the user's specialty
                return queryset.filter(specialist=specialist)
        return queryset.none()

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.specialist.user == request.user or request.user.is_superuser:
                return True
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.specialist.user == request.user or request.user.is_superuser:
                return True
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False


# Registering Specialist model in Django admin
@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'email', 'availability_start', 'availability_end', 'is_active')
    search_fields = ('name', 'specialty', 'email')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        # Only allow specialists to view their own profile
        return queryset.filter(user=request.user)

from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'reset_token', 'reset_token_expiry')  # Include 'specialty' in the list view
    search_fields = ('user__username', 'user__email')  # Make search fields available
    list_filter = ('specialty',)  # Allow filtering by 'specialty'
    fieldsets = (
        (None, {
            'fields': ('user', 'specialty', 'reset_token', 'reset_token_expiry')
        }),
    )

admin.site.register(UserProfile, UserProfileAdmin)