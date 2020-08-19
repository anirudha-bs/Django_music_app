from django.contrib.auth.models import Permission, User
from django.db import models

class Album(models.Model):

    user = models.ForeignKey(User, default=1,on_delete=models.CASCADE)
    artist = models.CharField(max_length=250)
    album_title = models.CharField(max_length=500)
    genre = models.CharField(max_length=100)
    album_logo = models.FileField(default="avatar.jpg")
    album_visibility = models.CharField(max_length=100, default="private")
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.album_title + '-' + self.artist + '-' + self.genre


class Song(models.Model):

    user = models.ForeignKey(User, default=1,on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    song_title = models.CharField(max_length=250)
    audio_file = models.FileField(default='')
    song_visibility = models.CharField(max_length=100, default="private")
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.song_title 