from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, \
                                  PageNotAnInteger
from common.decorators import ajax_required
from .forms import ImageCreateForm
from .models import Image
from .models import Picture
from .forms import PictureCreateForm
from actions.utils import create_action
import redis
from django.conf import settings


# Nawiązanie połączenia z bazą danych Redis.
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        # form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            new_item = form.save(commit=False)

            # assign current user to the item
            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Image added successfully')
            create_action(request.user, 'dodał obraz', new_item)
            # redirect to new created item detail view
            return redirect(new_item.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm()

    return render(request,
                  'images/image/create.html',
                  {'section': 'images',
                   'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # Inkrementacja o 1 całkowitej liczby wyświetleń danego obrazu.
    total_views = r.incr('image:{}:views'.format(image.id))
    # Inkrementacja o 1 rankingu danego obrazu.
    r.zincrby('image_ranking', image.id, 1)
    return render(request,
                  'images/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'polubił', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # If the request is AJAX and the page is out of range
            # return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        images = paginator.page(paginator.num_pages)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return render(request,
                      'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})
    return render(request,
                  'images/image/list.html',
                   {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    # Pobranie słownika rankingu obrazów.
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # Pobranie najczęściej wyświetlanych obrazów.
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))

    return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': most_viewed})


@login_required
def add_picture(request):
    if request.method == "POST":
        form = PictureCreateForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.save(commit=False)
            picture.user = request.user
            picture.save()

            # Getting the current instance object to display in the template
            # img_object = form.instance

            messages.success(request, 'Dodales pikczer')

            return redirect(picture.get_absolute_url())
        else:
            messages.error(request, 'Nie udalo sie')
    else:
        form = PictureCreateForm()

    return render(request, 'images/image/picture.html', {'section': 'picture', 'form': form})


def picture_detail(request, id, slug):
    picture = get_object_or_404(Picture, id=id, slug=slug)
    return render(request,
                  'images/image/picture_detail.html',
                  {'section': 'picture',
                   'picture': picture})


@login_required
def list_picture(request):
    picture = Picture.objects.all()
    return render(request, 'images/image/list_picture.html', {'section': 'picture', 'picture': picture})