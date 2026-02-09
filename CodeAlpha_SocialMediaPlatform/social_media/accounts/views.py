from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.db.models import Q

@login_required
def profile(request, username):
    user_profile = Profile.objects.get(user__username=username)
    current_user_profile = Profile.objects.get(user=request.user)
    is_following = request.user in user_profile.followers.all()

    if request.method == 'POST':
        if is_following:
            user_profile.followers.remove(request.user)
        else:
            user_profile.followers.add(request.user)
        return redirect('profile', username=username)

    return render(request, 'accounts/profile.html', {
        'user_profile': user_profile,
        'is_following': is_following
    })

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # automatically log in after registration
            return redirect('feed')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def edit_profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        profile.bio = request.POST.get('bio')
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES.get('profile_pic')
        profile.save()
        return redirect('profile', username=request.user.username)

    return render(request, 'accounts/edit_profile.html', {'profile': profile})

@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile

    if request.user in target_profile.followers.all():
        target_profile.followers.remove(request.user)
    else:
        target_profile.followers.add(request.user)

    return redirect('profile', username=username)

def search_users(request):
    query = request.GET.get('q')
    users = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query)
        )

    return render(request, 'accounts/search_results.html', {
        'users': users,
        'query': query
    })



    