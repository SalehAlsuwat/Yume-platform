from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomerSignUpForm, OwnerSignUpForm, SignInForm, UserEditForm, CustomerProfileEditForm, OwnerProfileEditForm
from .models import CustomerProfile, OwnerProfile, GROUP_CUSTOMER, GROUP_OWNER


def sign_up(request):
    return redirect('accounts:sign_up_guest')


def sign_up_guest(request):
    if request.user.is_authenticated:
        return redirect('main:home_view')

    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = GROUP_CUSTOMER
            user.save()
            CustomerProfile.objects.create(
                user=user,
                avatar=form.cleaned_data.get('avatar'),
            )
            login(request, user)
            return redirect('main:home_view')
    else:
        form = CustomerSignUpForm()

    return render(request, 'accounts/sign_up.html', {'form': form})


def sign_up_owner(request):
    if request.user.is_authenticated:
        return redirect('main:home_view')

    if request.method == 'POST':
        form = OwnerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = GROUP_OWNER
            user.save()
            OwnerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                commercial_reg=form.cleaned_data['commercial_reg'],
                avatar=form.cleaned_data.get('avatar'),
            )
            login(request, user)
            return redirect('main:home_view')
    else:
        form = OwnerSignUpForm()

    return render(request, 'accounts/sign_up_company.html', {'form': form})

def public_profile_view(request, username):
    profile = get_object_or_404(OwnerProfile, user__username=username, user__role=GROUP_OWNER)
    return render(request, 'accounts/company_profile.html', {'profile': profile})

def sign_in(request):
    if request.user.is_authenticated:
        return redirect('main:home_view')

    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'main:home_view')
                return redirect(next_url)
            messages.error(request, 'Invalid username or password.')
    else:
        form = SignInForm()

    return render(request, 'accounts/sign_in.html', {'form': form})


@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
    return redirect('main:home_view')

@login_required
def edit_profile(request):
    user = request.user
    ProfileForm = OwnerProfileEditForm if user.is_owner else CustomerProfileEditForm
    profile = user.owner_profile if user.is_owner else user.customer_profile

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:account_view')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })




@login_required
def account_view(request):
    return render(request, 'accounts/account.html')
