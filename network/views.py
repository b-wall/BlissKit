import json
import random

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count

from .models import User, Post

from .forms import PostForm


def index(request):
    """Show landing page"""
    # Randomly pull posts from database to display
    randomPosts = []
    for i in range(3):
        randomPost = random.choice(Post.objects.all())
        randomPosts.append(randomPost)
    return render(request, "network/index.html", {'randomPosts': randomPosts})


def login_view(request):
    """Show login page"""
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication is successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("allposts"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    """Logout User"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """Show register page"""
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("allposts"))
    else:
        return render(request, "network/register.html")


def allposts(request):
    """Display posts from all users"""
    if request.method == "POST":
        # Store data in database
        data = PostForm(request.POST)
        if data.is_valid():
            processData = data.save(commit=False)
            processData.user = request.user
            processData.save()
            return HttpResponseRedirect(reverse("allposts"))
    else:
        uid = request.user.id
        posts = Post.objects.all()
        pn = Paginator(posts, 10)
        page_no = request.GET.get('page')
        page = pn.get_page(page_no)
        return render(request, "network/allposts.html", {'PostForm': PostForm(), 'posts': posts, 'uid': uid, 'page': page})


@ login_required
def userprofile(request, uid):
    """Display user profile page"""
    userinfo = Post.objects.filter(user_id=uid)
    followers = User.objects.filter(pk=uid)
    user_profile = User.objects.get(pk=request.user.id)
    return render(request, "network/userprofile.html", {'uid': uid, 'userinfo': userinfo, 'user_profile': user_profile, 'followers': followers})


@ login_required
def following(request):
    """Display follower posts"""
    followers = request.user.followers.all()
    follower_posts = Post.objects.filter(user__in=followers)
    pn = Paginator(follower_posts, 10)
    page_no = request.GET.get('page')
    page = pn.get_page(page_no)
    return render(request, "network/following.html", {'follower_posts': follower_posts, 'page': page})


# API Routes

@csrf_exempt
@login_required
def follow(request, uid):
    """Follow/unfollow a user"""

    # Query for user
    try:
        current_user = User.objects.get(pk=request.user.id)
        followee = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Update user's follow status
    if request.method == "PUT":
        data = json.loads(request.body)
        # Check follow status and follow or unfollow user
        if data.get("followers") is not None:
            if followee in current_user.followers.all():
                current_user.followers.remove(followee.id)
                current_user.save()
                return JsonResponse({
                    "message": "Unfollowed."
                })
            else:
                current_user.followers.add(followee.id)
                current_user.save()
                return JsonResponse({
                    "message": "Followed."
                })

    # Request must be via PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)


@csrf_exempt
@login_required
def like_handle(request, post_id):
    """Like/unlike a user"""
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    # Check if request is correct, then change like/unlike value in database
    if request.method == 'PUT':
        data = json.loads(request.body)
        if data.get("liked") is not None:
            if data.get("liked") == True:
                post.likes.add(request.user)
                post.save()
                return JsonResponse({"message": "You have liked this post."})
            else:
                post.likes.remove(request.user)
                post.save()
                return JsonResponse({"message": "You have unliked this post."})
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@csrf_exempt
@login_required
def like_display(request):
    """Display likes on posts"""
    try:
        likes = request.user.likees.all()
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    if request.method == 'GET':
        return JsonResponse([like.serialize(request.user) for like in likes], safe=False)


@csrf_exempt
@login_required
def edit(request, post_id):
    """Edit functionality for user's posts"""
    # Query for user's post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == 'GET':
        return JsonResponse(post.serialize(request.user), safe=False)

    if request.method == 'PUT':
        # Check if user is the post owner
        if post.user == request.user:
            # Recieve edited data from user
            data = json.loads(request.body)
            editedContent = data.get("content", "")
            # Check server-side that message is less than 151 characters
            if len(editedContent) < 151:
                post.content = editedContent
                post.save()
                return JsonResponse({"message": "edited your post!"})
            else:
                return JsonResponse({"error": "edited post too long."})

    return JsonResponse(post.serialize(request.user), safe=False)
