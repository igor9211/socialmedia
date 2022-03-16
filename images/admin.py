from django.contrib import admin
from .models import Image
from .models import Picture


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'image', 'created']
    list_filter = ['created']


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created')