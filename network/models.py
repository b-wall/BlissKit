from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name="followees")

    def follower_count(self):
        return self.followers.all().count()

    def followee_count(self):
        return self.followees.all().count()

    def serialize(self):
        return {
            "uid": self.id,
            "followers": [{"id": follower.id} for follower in self.followers.all()]
        }


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="poster")
    content = models.TextField(max_length=150)
    time = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User, symmetrical=False, blank=True, related_name="likees")

    def like_count(self):
        return self.likes.all().count()

    def __str__(self):
        return f"{self.user} made a post at {self.time}."

    def serialize(self, user):
        if user in self.likes.all():
            liked = True
        else:
            liked = False
        return {
            "id": self.id,
            "content": self.content,
            "liked": liked,
            "likes": [{"id": like.id} for like in self.likes.all()],
            "like-count": self.like_count(),
            "timestamp": self.time.strftime("%b %d %Y, %I:%M %p")
        }

    # Order in reverse chronological order
    class Meta:
        ordering = ['-time']
