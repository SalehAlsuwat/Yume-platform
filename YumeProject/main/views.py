from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib import messages

from hotels.models import City
from .models import Contact
# Create your views here.

def error_404_view(request: HttpRequest, exception=None):
    return render(request, '404.html', status=404)

def home_view(request: HttpRequest):

    return render(request, 'main/home.html')

def about_view(request: HttpRequest):
    return render(request, 'main/about.html')

def contact_view(request:HttpRequest):
    if request.method == 'POST':
        Contact.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        
        messages.success(request, "Your message has been sent successfully!", "alert-success")

        return redirect('main:home_view')


    return render(request, 'main/contact.html')

def contact_view_all(request: HttpRequest):
    messages = Contact.objects.all().order_by('-created_at')
    return render(request, 'main/contact_view.html', {'messages': messages})

def contact_view_detail(request: HttpRequest, contact_id):
    message_detail = get_object_or_404(Contact, id=contact_id)
    return render(request, 'main/contact_details.html', {'message': message_detail})

def faq_view(request: HttpRequest):
    return render(request, 'main/faq.html')

def services_view(request: HttpRequest):
    return render(request, 'main/services.html')

def terms_privacy_view(request: HttpRequest):
    return render(request, 'main/terms_privacy.html')

def cities_view(request: HttpRequest):

    cities = City.objects.filter(is_active=True)
    city = City.objects.filter(name__iexact='Riyadh', is_active=True).first()

    return render(request, 'main/cities.html', {'cities': cities, 'city': city})


def mode_view(request, mode):

    next_url = request.GET.get("next", "/")

    if mode == "toggle":
        current_mode = request.COOKIES.get("mode", "light")
        mode = "dark" if current_mode == "light" else "light"

    response = redirect(next_url)
    response.set_cookie("mode", mode)

    return response

