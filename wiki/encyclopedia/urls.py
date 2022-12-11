from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("error", views.error, name="error"),
    path("search", views.search, name="search"),
    path("create", views.create, name="create"),
    path("<str:entry>/edit", views.edit, name="edit"),
    path("<str:entry>", views.openpage, name="openpage"),
    path("randompage/", views.randompage, name="randompage"),
        
]
