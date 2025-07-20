from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# -----------------------------
# User Profile Model
# -----------------------------
class Profile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('vendor', 'Vendor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.user.username


# -----------------------------
# Tour Package Model
# -----------------------------
class TourPackage(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    duration_days = models.PositiveIntegerField()
    image = models.ImageField(upload_to='package_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()


# -----------------------------
# Booking Model
# -----------------------------
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.tour_package.title}'
