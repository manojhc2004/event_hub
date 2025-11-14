from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path('register/', views.UserRegistrationView.as_view(), name='register'),

    # EVENTS
    path('', views.EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),

    # BOOKING
    path('event/<int:event_id>/confirm/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    #path("booking/<int:booking_id>/ticket/", views.download_ticket, name="download_ticket"),
    path("ticket/<int:booking_id>/download/", views.download_ticket, name="download_ticket"),

    # USER
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('profile/', views.UserProfileView.as_view(), name='profile_view'),

    # ADMIN
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]
