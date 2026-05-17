
from django.urls import path, include
from . import views

app_name="hotel_owner"

urlpatterns = [
    # ── Hotel ──
    path('', views.my_hotels, name='my_hotels'),
    path('owner/', views.owner_view, name='owner_view'),
    path('create/', views.hotel_create, name='hotel_create'),
    path('<int:pk>/update/', views.hotel_update, name='hotel_update'),
    path('<int:pk>/delete/', views.hotel_delete, name='hotel_delete'),

    # ── Capsule ──
    path('<int:hotel_pk>/capsules/', views.capsule_list, name='capsule_list'),
    path('<int:hotel_pk>/capsules/create/', views.capsule_create, name='capsule_create'),
    path('capsules/<int:pk>/update/', views.capsule_update, name='capsule_update'),
    path('capsules/<int:pk>/delete/', views.capsule_delete, name='capsule_delete'),  
]