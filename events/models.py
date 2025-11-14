from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

CATEGORY_CHOICES = (
    ('music', 'Music'),
    ('conference', 'Conference'),
    ('sports', 'Sports'),
    ('workshop', 'Workshop'),
)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    # NEW FIELDS
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='music')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    max_seats = models.IntegerField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def available_seats(self):
        booked_seats = self.booking_set.count()
        return self.max_seats - booked_seats

    def is_fully_booked(self):
        return self.available_seats() <= 0

    def __str__(self):
        return self.title



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"


# ✅ FINAL CORRECT SIGNAL
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # If user is newly created -> Create profile
    if created:
        UserProfile.objects.create(user=instance)
    # Always ensure profile exists (for older users)
    UserProfile.objects.get_or_create(user=instance)

# booking tickets
import uuid

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    # NEW FIELDS
    ticket_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    number_of_seats = models.IntegerField(default=1)  # 1 to 4 tickets

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
