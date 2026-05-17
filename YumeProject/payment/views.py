import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from booking.models import Booking

from .models import Payment
from .services import amount_to_minor_units, build_callback_url, fetch_payment, MoyasarError

logger = logging.getLogger(__name__)


def _allowed_payment_status(status):
    return status in {'paid', 'captured', 'verified'}


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer__user=request.user)

    if booking.status == Booking.STATUS_PAID:
        latest_payment = booking.payments.order_by('-created_at').first()
        return render(request, 'payment/result.html', {
            'success': True,
            'booking': booking,
            'payment': latest_payment,
        })

    payment_attempt = Payment.objects.create(
        booking=booking,
        amount=booking.total_price,
        currency=settings.MOYASAR_CURRENCY,
        status=Payment.STATUS_INITIATED,
    )

    callback_url = build_callback_url(request, booking.pk, payment_attempt.pk)
    description = f'Booking #{booking.pk} - {booking.capsule.hotel.name} / {booking.capsule.capsule_num}'

    context = {
        'booking': booking,
        'payment_attempt': payment_attempt,
        'publishable_key': settings.MOYASAR_PUBLISHABLE_KEY,
        'callback_url': callback_url,
        'amount_minor_units': amount_to_minor_units(booking.total_price),
        'currency': settings.MOYASAR_CURRENCY,
        'description': description,
        'payment_methods_json': json.dumps(['creditcard']),
        'supported_networks_json': json.dumps(['visa', 'mastercard', 'mada']),
    }
    return render(request, 'payment/checkout.html', context)


@login_required
def payment_callback_view(request):
    booking_id = request.GET.get('booking_id')
    payment_attempt_id = request.GET.get('payment_attempt_id')
    payment_id = request.GET.get('id')

    logger.info(f'Payment callback: booking_id={booking_id}, payment_attempt_id={payment_attempt_id}, payment_id={payment_id}')

    if not booking_id or not payment_attempt_id or not payment_id:
        logger.error('Payment verification data is missing.')
        messages.error(request, 'Payment verification data is missing.')
        return render(request, 'payment/result.html', {'success': False, 'booking': None, 'payment': None})

    booking = get_object_or_404(Booking, pk=booking_id, customer__user=request.user)
    payment_attempt = get_object_or_404(Payment, pk=payment_attempt_id, booking=booking)

    try:
        payment_data = fetch_payment(payment_id)
        logger.info(f'Payment data from Moyasar: {payment_data}')
    except MoyasarError as exc:
        logger.error(f'MoyasarError during fetch_payment: {str(exc)}')
        payment_attempt.status = Payment.STATUS_FAILED
        payment_attempt.raw_response = {'error': str(exc)}
        payment_attempt.save(update_fields=['status', 'raw_response', 'updated_at'])

        booking.status = Booking.STATUS_FAILED
        booking.save(update_fields=['status'])
        booking.capsule.is_available = True
        booking.capsule.save(update_fields=['is_available'])
        messages.error(request, 'We could not verify the payment.')
        return render(request, 'payment/result.html', {'success': False, 'booking': booking, 'payment': payment_attempt})

    expected_amount = amount_to_minor_units(booking.total_price)
    expected_currency = settings.MOYASAR_CURRENCY
    status = payment_data.get('status')
    amount = payment_data.get('amount')
    currency = payment_data.get('currency')
    
    logger.info(f'Verification check: status={status}, amount={amount} (expected {expected_amount}), currency={currency} (expected {expected_currency})')

    payment_attempt.provider_payment_id = payment_data.get('id') or payment_id
    payment_attempt.raw_response = payment_data

    if _allowed_payment_status(status) and amount == expected_amount and currency == expected_currency:
        payment_attempt.status = Payment.STATUS_PAID
        payment_attempt.paid_at = timezone.now()
        payment_attempt.verified_at = timezone.now()
        payment_attempt.save(update_fields=['provider_payment_id', 'raw_response', 'status', 'paid_at', 'verified_at', 'updated_at'])

        booking.status = Booking.STATUS_PAID
        booking.save(update_fields=['status'])
        booking.capsule.is_available = False
        booking.capsule.save(update_fields=['is_available'])

        messages.success(request, 'Payment confirmed successfully.')
        return render(request, 'payment/result.html', {'success': True, 'booking': booking, 'payment': payment_attempt})

    payment_attempt.status = Payment.STATUS_FAILED
    payment_attempt.save(update_fields=['provider_payment_id', 'raw_response', 'status', 'updated_at'])

    booking.status = Booking.STATUS_FAILED
    booking.save(update_fields=['status'])
    booking.capsule.is_available = True
    booking.capsule.save(update_fields=['is_available'])

    messages.error(request, 'The payment was not completed successfully.')
    return render(request, 'payment/result.html', {'success': False, 'booking': booking, 'payment': payment_attempt})