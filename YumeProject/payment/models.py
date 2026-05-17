import uuid

from django.db import models

from booking.models import Booking


class Payment(models.Model):
	STATUS_INITIATED = 'initiated'
	STATUS_PAID = 'paid'
	STATUS_FAILED = 'failed'
	STATUS_VERIFIED = 'verified'

	STATUS_CHOICES = [
		(STATUS_INITIATED, 'Initiated'),
		(STATUS_PAID, 'Paid'),
		(STATUS_FAILED, 'Failed'),
		(STATUS_VERIFIED, 'Verified'),
	]

	booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
	provider_name = models.CharField(max_length=50, default='moyasar')
	merchant_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	provider_payment_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	currency = models.CharField(max_length=3, default='SAR')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INITIATED)
	raw_response = models.JSONField(default=dict, blank=True)
	paid_at = models.DateTimeField(blank=True, null=True)
	verified_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
