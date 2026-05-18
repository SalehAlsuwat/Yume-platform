from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpRequest
from .models import City, CapsuleHotel, Capsule
from django.core.paginator import Paginator

# ── City Views ──

# Customer, Guest
def city_list(request):
    cities = City.objects.filter(is_active=True)
    return render(request, 'hotels/city_list.html', {'cities': cities})


# Customer, Guest
def hotel_list(request):
    hotels = CapsuleHotel.objects.filter(is_active=True)

    # ── Search ──
    q = request.GET.get('q')
    if q:
        hotels = hotels.filter(name__icontains=q)

    # ── City Filter ──
    city_name = request.GET.get('city')
    if city_name:
        hotels = hotels.filter(city__name__icontains=city_name)
    # city_id = request.GET.get('city')
    # if city_id:
    #     hotels = hotels.filter(city__id=city_id)

    # ── Price Filter ──
    price = request.GET.get('price')
    if price == 'low':
        hotels = hotels.filter(capsules__hour_price__lt=100).distinct()
    elif price == 'mid':
        hotels = hotels.filter(capsules__hour_price__range=(100, 300)).distinct()
    elif price == 'high':
        hotels = hotels.filter(capsules__hour_price__gt=300).distinct()

    # ── Pagination ──
    paginator = Paginator(hotels, 6)
    page_number = request.GET.get('page')
    hotels = paginator.get_page(page_number)

    cities = City.objects.filter(is_active=True)

    return render(request, 'hotels/hotel_list.html', {
        'hotels': hotels,
        'cities': cities,
    })


# Customer, Guest
def hotel_detail(request, pk):
    hotel = get_object_or_404(CapsuleHotel, pk=pk)
    capsules = hotel.capsules.filter(is_available=True)
    reviews = hotel.reviews.all().order_by('-created_at')[:5]

    related_hotels = CapsuleHotel.objects.filter(
        city=hotel.city,
        is_active=True
    ).exclude(pk=pk)[:3]

    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel,
        'capsules': capsules,
        'capsules_count': capsules.count(),
        'reviews': reviews,
        'related_hotels': related_hotels,
        'check_in': request.GET.get('check_in', ''),   # ← add
        'check_out': request.GET.get('check_out', ''), # ← add
        'capsules_qty': request.GET.get('capsules', 1),
    })