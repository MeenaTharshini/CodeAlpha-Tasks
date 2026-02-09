from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from accounts.models import Profile
from django.views.decorators.http import require_POST
from django.http import JsonResponse

def home(request):
    profile = Profile.objects.get(user=request.user)
    following_users = profile.following.all()

    posts = Post.objects.filter(user__in=following_users) | Post.objects.filter(user=request.user)
    posts = posts.order_by('-created_at')

    return render(request, 'posts/home.html', {'posts': posts})


@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/feed.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        Post.objects.create(user=request.user, content=content, image=image)
        return redirect('feed')
    return render(request, 'posts/create_post.html')


@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        'total_likes': post.likes.count(),
        'liked': liked
    })


@require_POST
@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get('comment')

        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )

        return JsonResponse({
            'username': request.user.username,
            'text': comment.text
        })