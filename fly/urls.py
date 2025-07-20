from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------
    # Home Page
    # -----------------------------
    path('', views.home, name='home'),

    # -----------------------------
    # User Authentication
    # -----------------------------
    path('user/register/', views.user_register, name='user_register'),
    path('user/login/', views.user_login, name='user_login'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),

    # -----------------------------
    # Vendor Authentication
    # -----------------------------
    path('vendor/register/', views.vendor_register, name='vendor_register'),
    path('vendor/login/', views.vendor_login, name='vendor_login'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/edit-package/<int:package_id>/', views.edit_package, name='edit_package'),

    # -----------------------------
    # Tour Package Management
    # -----------------------------
    path('add-package/', views.add_package, name='add_package'),
    path('packages/', views.package_list, name='package_list'),
    path('package/<int:pk>/', views.package_detail, name='package_detail'),

    # -----------------------------
    # Payment Handling
    # -----------------------------
    path('payment/success/', views.payment_success, name='payment_success'),

    # -----------------------------
    # Logout
    # -----------------------------
    path('logout/', views.user_logout, name='logout'),
]
