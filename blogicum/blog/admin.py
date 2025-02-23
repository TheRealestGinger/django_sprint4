from django.contrib import admin
from .models import Comment, Category, Post, Location

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Comment)
