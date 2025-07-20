from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User
from datetime import date
import razorpay
from .models import TourPackage, Booking, Profile

# -----------------------------
# Home Page
# -----------------------------
def home(request):
    return render(request, 'home.html')


# -----------------------------
# User Registration & Login
# -----------------------------
def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        image = request.FILES.get('image')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('user_register')

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = Profile.objects.create(user=user, role='user')
        if image:
            profile.image = image
            profile.save()

        login(request, user)
        messages.success(request, 'Registration successful.')
        return redirect('user_dashboard')

    return render(request, 'user_register.html')


def user_login(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=uname, password=pwd)
        if user and hasattr(user, 'profile') and user.profile.role == 'user':
            login(request, user)
            return redirect('user_dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'user_login.html')


# -----------------------------
# Vendor Registration & Login
# -----------------------------
def vendor_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('vendor_register')

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, role='vendor')
        messages.success(request, 'Vendor registered successfully. Please log in.')
        return redirect('vendor_login')

    return render(request, 'vendor_register.html')


def vendor_login(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=uname, password=pwd)
        if user and hasattr(user, 'profile') and user.profile.role == 'vendor':
            login(request, user)
            return redirect('vendor_dashboard')
        messages.error(request, 'Invalid vendor login.')
    return render(request, 'vendor_login.html')


# -----------------------------
# Logout
# -----------------------------
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')


# -----------------------------
# User Dashboard
# -----------------------------
@login_required
def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user).select_related('tour_package')

    available_packages = TourPackage.objects.filter(
        is_approved=True,
        end_date__gte=timezone.now().date()
    )

    active_bookings = bookings.filter(tour_package__end_date__gte=timezone.now().date())
    expired_bookings = bookings.filter(tour_package__end_date__lt=timezone.now().date())

    return render(request, 'user_dashboard.html', {
        'bookings': bookings,
        'available_packages': available_packages,
        'active_bookings': active_bookings,
        'expired_bookings': expired_bookings
    })


# -----------------------------
# Vendor Dashboard
# -----------------------------
@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'vendor':
        return redirect('vendor_login')

    packages = TourPackage.objects.filter(vendor=request.user)

    return render(request, 'vendor_dashboard.html', {'packages': packages})


# -----------------------------
# Add Tour Package (Vendor)
# -----------------------------
@login_required
def add_package(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        price = request.POST['price']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        duration_days = request.POST['duration_days']
        image = request.FILES.get('image')

        TourPackage.objects.create(
            title=title,
            description=description,
            price=price,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            image=image,
            vendor=request.user,
            is_approved=False
        )
        messages.success(request, "Package submitted for approval.")
        return redirect('vendor_dashboard')

    return render(request, 'add_package.html')


# -----------------------------
# Edit Tour Package (Vendor)
# -----------------------------
@login_required(login_url='vendor_login')
def edit_package(request, package_id):
    package = get_object_or_404(TourPackage, id=package_id, vendor=request.user)

    if request.method == 'POST':
        package.title = request.POST['title']
        package.description = request.POST['description']
        package.price = request.POST['price']
        package.start_date = request.POST['start_date']
        package.end_date = request.POST['end_date']
        package.duration_days = request.POST['duration_days']

        if 'image' in request.FILES:
            package.image = request.FILES['image']

        package.save()
        messages.success(request, 'Package updated successfully.')
        return redirect('vendor_dashboard')

    return render(request, 'edit_package.html', {'package': package})


# -----------------------------
# List Approved Tour Packages
# -----------------------------
def package_list(request):
    packages = TourPackage.objects.filter(is_approved=True, end_date__gte=timezone.now().date())
    return render(request, 'package_list.html', {'packages': packages})


# -----------------------------
# Tour Package Detail & Razorpay Payment
# -----------------------------
@login_required
def package_detail(request, pk):
    package = get_object_or_404(TourPackage, pk=pk, is_approved=True)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(package.price) * 100

    order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    context = {
        'package': package,
        'payment': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'order_amount': amount
    }
    return render(request, 'package_detail.html', context)


# -----------------------------
# Handle Razorpay Payment Success
# -----------------------------
@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        payment_id = request.POST.get('razorpay_payment_id')

        if not request.user.is_authenticated:
            return redirect('user_login')

        try:
            package = get_object_or_404(TourPackage, id=package_id)

            existing = Booking.objects.filter(user=request.user, tour_package=package).exists()
            if not existing:
                Booking.objects.create(
                    user=request.user,
                    tour_package=package,
                    payment_id=payment_id,
                    status='confirmed'
                )

            return render(request, 'payment_success.html')
        except Exception as e:
            print("Payment Success Error:", e)
            return redirect('package_list')
