from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import JsonResponse,HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from .models import Album, Song
from .forms import AlbumForm, SongForm, UserForm

AUDIO_FILE_TYPES = ['wav', 'mp3']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def index(request, filter_by='all', modifier='private'):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        if modifier == 'private':
            albums = Album.objects.filter(user=request.user)
            song_results = Song.objects.filter(user=request.user)
            query = request.GET.get("q")
            if query:
                albums = albums.filter(
                    Q(album_title__icontains=query) |
                    Q(artist__icontains=query)
                ).distinct()
                song_results = song_results.filter(
                    Q(song_title__icontains=query)
                ).distinct()
                return render(request, 'music/index.html', {
                    'albums': albums,
                    'songs': song_results,
                    'filter_by':filter_by, 
                    'modifier':modifier
                })
            elif filter_by == "favorites":
                albums = albums.filter(is_favorite=True)
                return render(request, 'music/index.html', {'albums': albums, 'filter_by':filter_by, 'modifier':modifier})
            else:
                return render(request, 'music/index.html', {'albums': albums, 'filter_by':filter_by, 'modifier':modifier})
        else:
            albums = Album.objects.filter(album_visibility="public")
            return render(request, 'music/index.html', {'albums': albums, 'filter_by':filter_by, 'modifier':modifier})


def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            albums = Album.objects.filter(user=request.user)
            return render(request,'music/index.html',{'albums': albums, 'filter_by':'all', 'modifier':'private'})

        else:
            return render(request, 'music/login.html', {'error_message': 'Invalid login'})
    return render(request, 'music/login.html')


def logout_user(request):

    logout(request)
    return render(request, 'music/login.html')


def register(request):

    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'albums': albums, 'filter_by':'all', 'modifier':'private'})
    context = {
        "form": form,
    }
    return render(request, 'music/register.html', context)


def detail(request, album_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        user = request.user
        albums = Album.objects.filter(user=request.user)
        album = get_object_or_404(albums, pk=album_id)
        return render(request, 'music/detail.html', {'album': album, 'albums':albums, 'user': user})        


def songs(request, filter_by, modifier='private'):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        if modifier == 'private':
            album = Album.objects.filter(user=request.user)
            songs = Song.objects.filter(user=request.user)
            if filter_by == 'favorites':
                songs = songs.filter(is_favorite=True)
            return render(request, 'music/songs.html', {'song_list':songs, 'filter_by':filter_by, 'modifier':modifier, 'albums':album})
        else:
            songs = Song.objects.filter(song_visibility="public")
            return render(request, 'music/songs.html', {'song_list':songs, 'filter_by':filter_by, 'modifier':modifier, 'albums':album})


def create_album(request):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.album_logo = request.FILES['album_logo']
            file_type = album.album_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'The image must be PNG, JPG or JPEG'
                }
                return render(request, 'music/create_album.html', context)
            album.save()
            return render(request,'music/detail.html',{'album': album})
    context = {
        "form": form
    }
    return render(request, 'music/create_album.html', context)


def create_song(request, album_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = SongForm(request.POST or None, request.FILES or None)
        album = get_object_or_404(Album, pk=album_id)
        if form.is_valid():
            albums_songs = album.song_set.all()
            for s in albums_songs:
                if s.song_title == form.cleaned_data.get("song_title"):
                    context = {
                        'album': album,
                        'form': form,
                        'error_message': 'You already added that song',
                    }
                    return render(request, 'music/create_song.html', context)
            song = form.save(commit=False)
            song.user = request.user
            song.album = album
            song.audio_file = request.FILES['audio_file']
            file_type = song.audio_file.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in AUDIO_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Audio file must be WAV, MP3, or OGG',
                }
                return render(request, 'music/create_song.html', context)

            song.save()
            return render(request, 'music/detail.html', {'album': album})
        context = {
            'album': album,
            'form': form,
        }
        return render(request, 'music/create_song.html', context)


def add_song(request):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        form = SongForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            song = form.save(commit=False)
            song.user = request.user
            song.audio_file = request.FILES['audio_file']
            file_type = song.audio_file.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in AUDIO_FILE_TYPES:
                context = {
                    'form': form,
                    'error_message': 'Audio file must be WAV, MP3, or OGG',
                }
                return render(request, 'music/add_song.html', context)
            song.save()
            return HttpResponseRedirect(reverse('music:songs',args=('all','private',)))
        context = {
            'form': form,
        }
        return render(request, 'music/add_song.html', context)


def favorite(request, song_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        song = get_object_or_404(Song.objects.filter(user=request.user), pk=song_id)
        try:
            if song.is_favorite:
                song.is_favorite = False
            else:
                song.is_favorite = True
            song.save()
        except (KeyError, Song.DoesNotExist):
            return JsonResponse('Song does not exist')
        else:
            return HttpResponseRedirect(reverse('music:songs',args=('all','private',)))


def favorite_album(request, album_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        album = get_object_or_404(Album.objects.filter(user=request.user), pk=album_id)
        try:
            if album.is_favorite:
                album.is_favorite = False
            else:
                album.is_favorite = True
            album.save()
        except (KeyError, Album.DoesNotExist):
            return JsonResponse('Album does not exist')
        else:
            return HttpResponseRedirect(reverse('music:index',args=('all','private',)))


def album_modify(request, album_id, modifier):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        album = get_object_or_404(Album.objects.filter(user=request.user), pk=album_id) 
        album.album_visibility = modifier
        album.save()
        return HttpResponseRedirect(reverse('music:index',args=('all','private',)))


def song_modify(request, song_id, modifier):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        song = get_object_or_404(Song.objects.filter(user=request.user), pk=song_id) 
        song.song_visibility = modifier
        song.save()
        albums = Album.objects.filter(user=request.user)
        return HttpResponseRedirect(reverse('music:songs',args=('all','private',albums,)))


def move_song(request, song_id, album_title):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        song = get_object_or_404(Song.objects.filter(user=request.user), pk=song_id) 
        album = get_object_or_404(Album.objects.filter(user=request.user,album_title = album_title))
        song.album = album
        song.save()
        return HttpResponseRedirect(reverse('music:songs',args=('all','private',)))


def copy_song(request, song_id, album_title):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        song = get_object_or_404(Song.objects.filter(user=request.user, pk=song_id))
        album = get_object_or_404(Album.objects.filter(user=request.user,album_title=album_title))
        temp_song = Song()
        temp_song.user = song.user
        temp_song.album = album
        temp_song.song_title = song.song_title
        temp_song.audio_file = song.audio_file
        temp_song.save()
        return HttpResponseRedirect(reverse('music:songs',args=('all','private',)))


def delete_album(request, album_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        album = Album.objects.get(pk=album_id)
        albums = Album.objects.filter(user=request.user)
        if album.user == request.user:
            album.delete()
            return render(request, 'music/index.html', {'albums': albums, 'filter_by':'all', 'modifier':'private'})
        else:
            return JsonResponse({'Error':'Not allowed'})


def delete_song(request, album_id, song_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        album = get_object_or_404(Album.objects.filter(user=request.user), pk=album_id)
        song = Song.objects.get(pk=song_id)
        if song.user == request.user:
            song.delete()
            return render(request, 'music/detail.html', {'album': album})
        else:
            return JsonResponse({'Error':'Not allowed'})

def del_song(request, song_id):

    if not request.user.is_authenticated:
        return render(request, 'music/login.html')
    else:
        song = Song.objects.get(pk=song_id)
        if song.user == request.user:
            song.delete()
            return HttpResponseRedirect(reverse('music:songs',args=('all','private',)))
        else:
            return JsonResponse({'Error':'Not allowed'})
