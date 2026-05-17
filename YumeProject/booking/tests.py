from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomerProfile, OwnerProfile, User, GROUP_CUSTOMER, GROUP_OWNER
from hotels.models import CapsuleHotel, Capsule, City
from booking.models import Booking


class BookingFlowTests(TestCase):
	def setUp(self):
		self.customer_user = User.objects.create_user(
			username='customer1',
			password='pass12345',
			role=GROUP_CUSTOMER,
		)
		CustomerProfile.objects.create(user=self.customer_user, phone_number='0500000000')

		self.owner_user = User.objects.create_user(
			username='owner1',
			password='pass12345',
			role=GROUP_OWNER,
		)
		self.owner_profile = OwnerProfile.objects.create(
			user=self.owner_user,
			company_name='Yume Owner',
			commercial_reg='1234567890',
			phone_number='0500000001',
		)

		self.city = City.objects.create(name='Riyadh')
		self.hotel = CapsuleHotel.objects.create(
			name='Sky Capsule Hotel',
			description='Test hotel',
			address='Main street',
			image=SimpleUploadedFile('hotel.jpg', b'test-image', content_type='image/jpeg'),
			rating=4.5,
			is_active=True,
			hotel_owner=self.owner_profile,
			city=self.city,
		)
		self.capsule = Capsule.objects.create(
			hotel=self.hotel,
			hour_price=Decimal('100.00'),
			night_price=Decimal('300.00'),
			is_available=True,
			capsule_num='C-101',
		)

	def test_booking_post_creates_pending_booking_and_redirects_to_payment(self):
		self.client.force_login(self.customer_user)

		response = self.client.post(
			reverse('booking:booking_view', args=[self.hotel.pk]),
			{
				'capsule_id': self.capsule.pk,
				'booking_type': 'hour',
				'quantity': 2,
			},
		)

		self.assertEqual(response.status_code, 302)
		booking = Booking.objects.get()
		self.assertEqual(response.url, reverse('payment:payment', args=[booking.pk]))

		self.assertEqual(booking.status, Booking.STATUS_PENDING)
		self.assertEqual(booking.quantity, 2)
		self.assertEqual(booking.total_price, Decimal('200.00'))
		self.capsule.refresh_from_db()
		self.assertFalse(self.capsule.is_available)
