from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import TourPackage, Booking, Profile

# -----------------------------
# Profile Inline for User Admin
# -----------------------------
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# -----------------------------
# Custom User Admin with Profile
# -----------------------------
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)


# Unregister default User and register customized UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# -----------------------------
# Profile Admin
# -----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


# -----------------------------
# TourPackage Admin
# -----------------------------
@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'start_date', 'end_date', 'is_expired_display')
    list_filter = ('is_approved', 'start_date')
    search_fields = ('title', 'description', 'created_by__username')
    actions = ['approve_packages', 'disapprove_packages']

    def is_expired_display(self, obj):
        return obj.is_expired
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Expired'

    def approve_packages(self, request, queryset):
        queryset.update(is_approved=True)
    approve_packages.short_description = "Mark selected packages as approved"

    def disapprove_packages(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_packages.short_description = "Mark selected packages as disapproved"


# -----------------------------
# Booking Admin
# -----------------------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour_package', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'tour_package__title')
    ordering = ('-created_at',)