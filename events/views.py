from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.db.models import Count, Q 
from datetime import date
from .models import Event, Booking, UserProfile 
# FIX IS HERE: Importing the correct, renamed forms.
from .forms import UserUpdateForm, ProfileUpdateForm 
from reportlab.pdfgen import canvas

# ----------------------------------------------------
# 1. AUTHENTICATION (Registration)
# ----------------------------------------------------
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomRegisterForm
from datetime import datetime, time
from django.utils import timezone
from datetime import date, datetime
from django.utils import timezone
from datetime import date, timedelta





class UserRegistrationView(View):
    """Handles new user registration."""

    def get(self, request):
        form = CustomRegisterForm()
        return render(request, "registration/register.html", {"form": form})

    def post(self, request):
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now login.")
            return redirect("login")

        return render(request, "registration/register.html", {"form": form})



# ----------------------------------------------------
# 2. EVENT LISTING (Landing Page) - Includes Search Logic
# ----------------------------------------------------
class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        queryset = Event.objects.all()

        # 1️⃣ Search filter
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(venue__icontains=q)
            )

        # 2️⃣ Category filter
        selected_category = self.request.GET.get("category", "all")
        if selected_category and selected_category != "all":
            queryset = queryset.filter(category=selected_category)

        # 3️⃣ Price filter
        selected_price = self.request.GET.get("price")
        if selected_price:
            try:
                queryset = queryset.filter(price__lte=int(selected_price))
            except ValueError:
                pass

        return queryset.order_by("date", "time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Send selected filters back to template
        context["selected_category"] = self.request.GET.get("category", "all")
        context["selected_price"] = self.request.GET.get("price", "")

        #  Category List (for filter bar)
        context["category_list"] = [
            ("all", "All"),
            ("music", "Music"),
            ("conference", "Conference"),
            ("sports", "Sports"),
            ("workshop", "Workshop"),
        ]

        return context




# ----------------------------------------------------
# 3. EVENT DETAILS AND BOOKING
# ----------------------------------------------------

class EventDetailView(DetailView):
    """Displays a single event and its details."""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        if self.request.user.is_authenticated:
            context['has_booked'] = Booking.objects.filter(
                user=self.request.user, 
                event=event
            ).exists()
        return context

class BookEventView(LoginRequiredMixin, View):
    """Handles the booking submission."""
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.date < date.today():
            messages.error(request, 'Cannot book an event that has already passed.')
            return redirect('event_detail', pk=event.pk)

        if event.is_fully_booked():
            messages.error(request, f'{event.title} is fully booked. Sorry!')
            return redirect('event_detail', pk=event.pk)

        if Booking.objects.filter(user=request.user, event=event).exists():
            messages.warning(request, f'You have already booked a seat for {event.title}.')
            return redirect('event_detail', pk=event.pk)

        try:
            Booking.objects.create(user=request.user, event=event)
            messages.success(request, f'Successfully booked a seat for {event.title}!')
            return redirect('booking_confirmation', pk=event.pk)
        except Exception as e:
            messages.error(request, f'An error occurred during booking: {e}')
            return redirect('event_detail', pk=event.pk)
        

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Event, Booking

@login_required(login_url='login')
def booking_confirmation(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # FULL CHECK
    if event.is_fully_booked():
        messages.error(request, "This event is fully booked.")
        return redirect("event_detail", pk=event_id)

    # DUPLICATE CHECK
    if Booking.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You already booked this event.")
        return redirect("event_detail", pk=event_id)

    # CREATE BOOKING
    booking = Booking.objects.create(
        user=request.user,
        event=event
    )

    return render(request, "events/booking_confirmation.html", {
        "event": event,
        "booking": booking,
    })






# ----------------------------------------------------
# 4. USER BOOKINGS
# ------------
from datetime import datetime
from django.utils import timezone

class MyBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'events/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related("event").order_by('-booking_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for booking in context["bookings"]:
            event_datetime = timezone.make_aware(
                datetime.combine(booking.event.date, booking.event.time)
            )
            booking.can_cancel = timezone.now() < event_datetime

        return context




# ----------------------------------------------------
# 5. USER PROFILE (Enhanced with ProfilePicture/Mobile)
# ----------------------------------------------------

class UserProfileView(LoginRequiredMixin, View):
    """Displays the user profile and handles form submission for updates."""

    def get(self, request):
        # Forms
        user_form = UserUpdateForm(instance=request.user)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)

        # USER BOOKINGS (FIX IS HERE)
        bookings = Booking.objects.filter(user=request.user).select_related("event").order_by('-booking_date')

        upcoming = []
        past = []

        from datetime import date
        for booking in bookings:
            if booking.event.date >= date.today():
                upcoming.append(booking)
            else:
                past.append(booking)

        return render(request, 'events/profile.html', {
            'user_form': user_form,
            'profile_form': profile_form,
            'bookings': bookings,
            'upcoming_bookings': upcoming,
            'past_bookings': past,
        })

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        user_profile = request.user.userprofile
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_view')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = {
                'user_form': user_form,
                'profile_form': profile_form
            }
            return render(request, 'events/profile.html', context)


# ----------------------------------------------------
# 6. ADMIN DASHBOARD
# ----------------------------------------------------

def is_superuser(user):
    return user.is_superuser

@method_decorator(user_passes_test(is_superuser, login_url='/admin/login/'), name='dispatch')
class AdminDashboardView(LoginRequiredMixin, View):
    """Displays core statistics for administrators."""
    def get(self, request):
        total_events = Event.objects.count()
        total_bookings = Booking.objects.count()
        total_users = User.objects.count()
        
        recent_bookings = Booking.objects.select_related('user', 'event').order_by('-booking_date')[:5]
        
        event_stats = Event.objects.annotate(
            num_bookings=Count('booking')
        ).order_by('-num_bookings')[:5]

        context = {
            'total_events': total_events,
            'total_bookings': total_bookings,
            'total_users': total_users,
            'recent_bookings': recent_bookings,
            'event_stats': event_stats,
        }
        return render(request, 'events/admin_dashboard.html', context)


from django.utils import timezone

@login_required
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    event = booking.event

    now = timezone.now()

    # Correct datetime combine
    event_datetime = timezone.make_aware(
        datetime.combine(event.date, event.time)
    )

    if now >= event_datetime:
        messages.error(request, "You cannot cancel this booking because the event has already started or passed.")
        return redirect("my_bookings")

    # Delete booking only
    booking.delete()

    messages.success(request, f"Your booking for '{event.title}' has been cancelled.")
    return redirect("my_bookings")



from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse

@login_required
def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # PDF response
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.ticket_id}.pdf"'

    # Create PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "🎟 Event Ticket")

    p.setFont("Helvetica", 14)
    p.drawString(50, height - 100, f"Event: {booking.event.title}")
    p.drawString(50, height - 130, f"Date: {booking.event.date}")
    p.drawString(50, height - 160, f"Time: {booking.event.time}")
    p.drawString(50, height - 190, f"Venue: {booking.event.venue}")

    p.drawString(50, height - 230, f"Ticket ID: {booking.ticket_id}")
    p.drawString(50, height - 260, f"Seats Booked: {booking.number_of_seats}")

    p.drawString(50, height - 310, "Thank you for booking with EventHub! ❤️")

    p.showPage()
    p.save()
    return response

