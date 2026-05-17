from decimal import Decimal
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomerProfile, OwnerProfile, User, GROUP_CUSTOMER, GROUP_OWNER
from booking.models import Booking
from hotels.models import CapsuleHotel, Capsule, City
from payment.models import Payment
from payment.services import MoyasarError


@override_settings(MOYASAR_PUBLISHABLE_KEY='pk_test_123', MOYASAR_SECRET_KEY='sk_test_123')
class PaymentFlowTests(TestCase):
	def setUp(self):
		self.customer_user = User.objects.create_user(
			username='customer2',
			password='pass12345',
			role=GROUP_CUSTOMER,
		)
		CustomerProfile.objects.create(user=self.customer_user, phone_number='0500000000')

		self.owner_user = User.objects.create_user(
			username='owner2',
			password='pass12345',
			role=GROUP_OWNER,
		)
		self.owner_profile = OwnerProfile.objects.create(
			user=self.owner_user,
			company_name='Yume Owner 2',
			commercial_reg='1234567891',
			phone_number='0500000001',
		)

		self.city = City.objects.create(name='Jeddah')
		self.hotel = CapsuleHotel.objects.create(
			name='Sea Capsule Hotel',
			description='Test hotel',
			address='Coast road',
			image=SimpleUploadedFile('hotel.jpg', b'test-image', content_type='image/jpeg'),
			rating=4.2,
			is_active=True,
			hotel_owner=self.owner_profile,
			city=self.city,
		)
		self.capsule = Capsule.objects.create(
			hotel=self.hotel,
			hour_price=Decimal('120.00'),
			night_price=Decimal('350.00'),
			is_available=True,
			capsule_num='C-202',
		)
		self.booking = Booking.objects.create(
			check_in=timezone.now(),
			check_out=timezone.now(),
			quantity=2,
			total_price=Decimal('240.00'),
			commission_amount=Decimal('0.00'),
			commission_rate=Decimal('0.00'),
			booking_type='hour',
			status=Booking.STATUS_PENDING,
			customer=self.customer_user.customer_profile,
			capsule=self.capsule,
		)

	def test_payment_checkout_page_renders_moyasar_form(self):
		self.client.force_login(self.customer_user)

		response = self.client.get(reverse('payment:payment', args=[self.booking.pk]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'pk_test_123')
		self.assertEqual(Payment.objects.count(), 1)

	@patch('payment.views.fetch_payment')
	def test_callback_marks_booking_paid_when_moyasar_returns_paid_payment(self, mock_fetch_payment):
		self.client.force_login(self.customer_user)
		self.client.get(reverse('payment:payment', args=[self.booking.pk]))
		payment_attempt = Payment.objects.latest('created_at')

		mock_fetch_payment.return_value = {
			'id': 'moyasar-payment-1',
			'status': 'paid',
			'amount': 24000,
			'currency': 'SAR',
		}

		response = self.client.get(
			reverse('payment:callback'),
			{
				'booking_id': self.booking.pk,
				'payment_attempt_id': payment_attempt.pk,
				'id': 'moyasar-payment-1',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.booking.refresh_from_db()
		self.capsule.refresh_from_db()
		payment_attempt.refresh_from_db()

		self.assertEqual(self.booking.status, Booking.STATUS_PAID)
		self.assertEqual(payment_attempt.status, Payment.STATUS_PAID)
		self.assertFalse(self.capsule.is_available)

	@patch('payment.views.fetch_payment')
	def test_callback_marks_booking_failed_when_moyasar_verification_fails(self, mock_fetch_payment):
		self.client.force_login(self.customer_user)
		self.client.get(reverse('payment:payment', args=[self.booking.pk]))
		payment_attempt = Payment.objects.latest('created_at')

		mock_fetch_payment.side_effect = MoyasarError('network error')

		response = self.client.get(
			reverse('payment:callback'),
			{
				'booking_id': self.booking.pk,
				'payment_attempt_id': payment_attempt.pk,
				'id': 'moyasar-payment-2',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.booking.refresh_from_db()
		self.capsule.refresh_from_db()
		payment_attempt.refresh_from_db()

		self.assertEqual(self.booking.status, Booking.STATUS_FAILED)
		self.assertEqual(payment_attempt.status, Payment.STATUS_FAILED)
		self.assertTrue(self.capsule.is_available)
