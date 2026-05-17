from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from hotels.models import CapsuleHotel


@login_required
def add_review_view(request):

    if request.method == 'POST':

        hotel_id = request.POST.get('hotel_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        hotel = get_object_or_404(CapsuleHotel, id=hotel_id)

        Review.objects.create(
            user=request.user,
            hotel=hotel,
            rating=rating,
            comment=comment
        )

        return redirect('hotels:hotel_detail', pk=hotel.id)
    

@login_required
def delete_review(request, pk):

    if not request.user.is_superuser:
        return redirect('/')

    review = get_object_or_404(Review, pk=pk)

    hotel_id = review.hotel.id
    username = review.user.username

    review.delete()

    messages.success(
        request,
        f"Review by {username} deleted successfully."
    )

    return redirect('hotels:hotel_detail', pk=hotel_id)