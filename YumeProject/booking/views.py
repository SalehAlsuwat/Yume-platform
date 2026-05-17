from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomerProfile
from hotels.models import CapsuleHotel, Capsule

from .forms import BookingRequestForm
from .models import Booking


def _customer_profile_for_user(user):
    try:
        return user.customer_profile
    except CustomerProfile.DoesNotExist:
        return None


@login_required
def booking_view(request, pk):
    hotel = get_object_or_404(CapsuleHotel, pk=pk, is_active=True)

    if not request.user.is_customer:
        messages.error(request, 'Only customers can book capsules.')
        return redirect('accounts:account_view')

    if request.method != 'POST':
        messages.info(request, 'Choose a capsule and start booking from the hotel page.')
        return redirect('hotels:hotel_detail', pk=hotel.pk)

    form = BookingRequestForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please review the booking details and try again.')
        return redirect('hotels:hotel_detail', pk=hotel.pk)

    capsule = get_object_or_404(
        Capsule,
        pk=form.cleaned_data['capsule_id'],
        hotel=hotel,
        is_available=True,
    )

    quantity = form.cleaned_data['quantity']
    booking_type = form.cleaned_data['booking_type']
    check_in = timezone.now()
    duration = timedelta(hours=quantity) if booking_type == 'hour' else timedelta(days=quantity)
    check_out = check_in + duration
    unit_price = capsule.hour_price if booking_type == 'hour' else capsule.night_price
    total_price = (Decimal(unit_price) * Decimal(quantity)).quantize(Decimal('0.01'))
    customer_profile = _customer_profile_for_user(request.user)

    if customer_profile is None:
        messages.error(request, 'Your customer profile is missing. Please sign in again or contact support.')
        return redirect('accounts:sign_in')

    with transaction.atomic():
        capsule = Capsule.objects.select_for_update().get(pk=capsule.pk)
        if not capsule.is_available:
            messages.error(request, 'That capsule is no longer available.')
            return redirect('hotels:hotel_detail', pk=hotel.pk)

        booking = Booking.objects.create(
            check_in=check_in,
            check_out=check_out,
            quantity=quantity,
            total_price=total_price,
            commission_amount=Decimal('0.00'),
            commission_rate=Decimal('0.00'),
            booking_type=booking_type,
            status=Booking.STATUS_PENDING,
            customer=customer_profile,
            capsule=capsule,
        )

        capsule.is_available = False
        capsule.save(update_fields=['is_available'])

    messages.success(request, 'Booking created. Complete payment to confirm it.')
    return redirect(reverse('payment:payment', args=[booking.pk]))