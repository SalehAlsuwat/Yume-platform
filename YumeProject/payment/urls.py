from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('<int:booking_id>/', views.payment_view, name='payment'),
    path('callback/', views.payment_callback_view, name='callback'),
]
