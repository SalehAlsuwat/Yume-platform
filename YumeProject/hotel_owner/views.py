from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,HttpRequest
from accounts.decorators import owner_required
from hotels.models import CapsuleHotel, Capsule
from .forms import CapsuleHotelForm, CapsuleForm




@owner_required
def owner_view(request):
    return HttpResponse("Owner dashboard — coming soon.")

# ── Hotel Views ──

# Hotel Owner
def hotel_create(request):
    if request.method == 'POST':
        form = CapsuleHotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.hotel_owner = request.user.owner_profile
            hotel.is_active = False  # waiting for admin approval
            hotel.save()
            return redirect('hotel_owner:my_hotels')
    else:
        form = CapsuleHotelForm()
    return render(request, 'hotel_owner/hotel_form.html', {'form': form})


# Hotel Owner
def my_hotels(request):
    hotels = CapsuleHotel.objects.filter(
        hotel_owner=request.user.owner_profile
    )
    return render(request, 'hotel_owner/my_hotels.html', {'hotels': hotels})


# Hotel Owner
def hotel_update(request, pk):
    hotel = get_object_or_404(CapsuleHotel, pk=pk)
    if request.method == 'POST':
        form = CapsuleHotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('hotel_owner:my_hotels')
    else:
        form = CapsuleHotelForm(instance=hotel)
    return render(request, 'hotel_owner/hotel_form.html', {'form': form})


# Hotel Owner
def hotel_delete(request, pk):
    hotel = get_object_or_404(CapsuleHotel, pk=pk)
    if request.method == 'POST':
        hotel.delete()
        return redirect('hotel_owner:my_hotels')
    return render(request, 'hotel_owner/hotel_confirm_delete.html', {'hotel': hotel})


# ── Capsule Views ──

# Hotel Owner
def capsule_list(request, hotel_pk):
    hotel = get_object_or_404(CapsuleHotel, pk=hotel_pk)
    capsules = hotel.capsules.all()
    return render(request, 'hotel_owner/capsule_list.html', {
        'hotel': hotel,
        'capsules': capsules,
        'available_count': capsules.filter(is_available=True).count(),
        'booked_count': capsules.filter(is_available=False).count(),
    })


# Hotel Owner
def capsule_create(request, hotel_pk):
    hotel = get_object_or_404(CapsuleHotel, pk=hotel_pk)
    if request.method == 'POST':
        form = CapsuleForm(request.POST)
        if form.is_valid():
            count = form.cleaned_data['capsule_count']
            hour_price = form.cleaned_data['hour_price']
            night_price = form.cleaned_data['night_price']

            last_capsule = Capsule.objects.filter(hotel=hotel).order_by('-id').first()
            if last_capsule:
                last_num = int(last_capsule.capsule_num.split('-')[1])
            else:
                last_num = 0

            # existing_count = Capsule.objects.filter(hotel=hotel).count()
            for i in range(1, count + 1):
                Capsule.objects.create(
                    hotel=hotel,
                    capsule_num=f"{hotel.id}-{last_num + i}",
                    hour_price=hour_price,
                    night_price=night_price,
                )
            return redirect('hotel_owner:capsule_list', hotel_pk=hotel_pk)
    else:
        form = CapsuleForm()
    return render(request, 'hotel_owner/capsule_form.html', {
        'form': form,
        'hotel': hotel,
    })


# Hotel Owner
def capsule_update(request, pk):
    capsule = get_object_or_404(Capsule, pk=pk)
    if request.method == 'POST':
        form = CapsuleForm(request.POST, instance=capsule)
        if form.is_valid():
            form.save()
            return redirect('hotel_owner:capsule_list', hotel_pk=capsule.hotel.pk)
    else:
        form = CapsuleForm(instance=capsule)
    return render(request, 'hotel_owner/capsule_form.html', {
        'form': form,
        'hotel': capsule.hotel,
    })


# Hotel Owner
def capsule_delete(request, pk):
    capsule = get_object_or_404(Capsule, pk=pk)
    hotel_pk = capsule.hotel.pk
    if request.method == 'POST':
        capsule.delete()
        return redirect('hotel_owner:capsule_list', hotel_pk=hotel_pk)
    return render(request, 'hotel_owner/capsule_list.html', {
        'capsule': capsule,
    })