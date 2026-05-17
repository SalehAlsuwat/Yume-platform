import base64
import json
import logging
from decimal import Decimal, ROUND_HALF_UP
from urllib import error, parse, request

from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


class MoyasarError(RuntimeError):
    pass


def amount_to_minor_units(amount):
    return int((Decimal(amount).quantize(Decimal('0.01')) * 100).to_integral_value(rounding=ROUND_HALF_UP))


def build_callback_url(request_obj, booking_id, payment_attempt_id):
    callback_path = reverse('payment:callback')
    query_string = parse.urlencode({
        'booking_id': booking_id,
        'payment_attempt_id': payment_attempt_id,
    })
    return request_obj.build_absolute_uri(f'{callback_path}?{query_string}')


def _basic_auth_header(secret_key):
    token = base64.b64encode(f'{secret_key}:'.encode('utf-8')).decode('ascii')
    return f'Basic {token}'


def fetch_payment(payment_id):
    if not settings.MOYASAR_SECRET_KEY:
        raise MoyasarError('MOYASAR_SECRET_KEY is not configured.')

    url = f'{settings.MOYASAR_API_BASE_URL}/payments/{payment_id}'
    auth_header = _basic_auth_header(settings.MOYASAR_SECRET_KEY)
    
    logger.info(f'Fetching payment from Moyasar: URL={url}')
    logger.info(f'Authorization header: {auth_header[:20]}...')
    
    req = request.Request(
        url,
        headers={
            'Accept': 'application/json',
            'Authorization': auth_header,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        },
        method='GET',
    )

    try:
        with request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode('utf-8'))
            logger.info(f'Payment fetched successfully: {result}')
            return result
    except error.HTTPError as exc:
        logger.error(f'HTTP {exc.code} error from Moyasar')
        logger.error(f'Response: {exc.read().decode("utf-8")}')
        raise MoyasarError(f'Failed to verify payment with Moyasar: {exc.code}') from exc
    except error.URLError as exc:
        raise MoyasarError('Could not reach Moyasar.') from exc