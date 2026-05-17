from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('',                 views.account_view,  name='account_view'),
    path('sign-up/',         views.sign_up,        name='sign_up'),
    path('sign-up/guest/',   views.sign_up_guest,  name='sign_up_guest'),
    path('sign-up/owner/',   views.sign_up_owner,  name='sign_up_owner'),
    path('sign-in/',         views.sign_in,        name='sign_in'),
    path('sign-out/',              views.sign_out,            name='sign_out'),
    path('edit-profile/',          views.edit_profile,        name='edit_profile'),
    path('profile/<str:username>/', views.public_profile_view, name='public_profile'),
    
]
