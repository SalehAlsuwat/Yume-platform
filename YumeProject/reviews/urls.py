from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [

    path('add/', views.add_review_view, name='add_review_view'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),

]