from django.contrib import admin
from .models import User, Categorie, Listing, Watchlist, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Categorie)
admin.site.register(Listing)
admin.site.register(Watchlist)
admin.site.register(Comment)