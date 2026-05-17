from accounts.decorators import admin_role_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from hotels.models import CapsuleHotel, City
from accounts.models import OwnerProfile
from main.models import Contact
from .forms import CityForm

User = get_user_model()


@admin_role_required
def admin_view(request):
    context = {
        'pending_hotels':    CapsuleHotel.objects.filter(is_active=False).select_related('hotel_owner', 'city'),
        'approved_hotels':   CapsuleHotel.objects.filter(is_active=True).select_related('hotel_owner', 'city'),
        'all_users':         User.objects.all().order_by('date_joined'),
        'owners':            OwnerProfile.objects.all().select_related('user'),
        'cities':            City.objects.all(),
        'contact_requests':  Contact.objects.all().order_by('-created_at'),
    }
    return render(request, 'administration/dashboard.html', context)


@admin_role_required
def add_city(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('administration:admin_view')


@admin_role_required
def toggle_hotel(request, hotel_id):
    if request.method == 'POST':
        hotel = get_object_or_404(CapsuleHotel, pk=hotel_id)
        hotel.is_active = not hotel.is_active
        hotel.save()
    return redirect('administration:admin_view')
