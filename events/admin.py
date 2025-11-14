from django.contrib import admin
from .models import Event, Booking
from django.contrib import admin
from .models import Event, Booking, UserProfile

from django.contrib import admin
from .models import Event, Booking, UserProfile

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'date', 'venue', 'max_seats')
    list_filter = ('category', 'date')
    search_fields = ('title', 'venue', 'description')




@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "booking_date")
    list_filter = ("event", "booking_date")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile")
