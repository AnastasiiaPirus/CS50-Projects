from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Categorie, Listing, Watchlist, Comment

import json

def index(request):
    if request.method == "POST" and "filter" in request.POST:
        category = request.POST["filter"]
        return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(category=category),
        "categories": Categorie.objects.all(),
        })
    else:
        return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "categories": Categorie.objects.all(),
        })
def watchlist(request):
    watchlist = Watchlist.objects.filter(user_id=request.user.id)
    user_watchlist = []
    for i in range(len(watchlist)):
        user_watchlist.append(watchlist[i].listing_id)
    listings = Listing.objects.filter(id__in=user_watchlist)

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def listing(request, listing):
    user_id = request.user.id
    ls = Listing.objects.get(title=listing)
    listing_id = ls.id
    seller_id = ls.seller_id
    active = ls.active
    highest_bid_id = ls.highest_bid_id
    comment_list = Comment.objects.filter(listing_id = listing_id)
    comment_text = []
    comment_author_name = []
    for i in range(len(comment_list)):
        comment_text.append(comment_list[i].text)
        comment_author_id = comment_list[i].author_id
        comment_author = User.objects.get(id=comment_author_id)
        comment_author = comment_author.username
        comment_author_name.append(comment_author)
    try: 
        user_watchlist = Watchlist.objects.get(user_id=request.user.id, listing_id=listing_id)        
    except: 
        user_watchlist = None
        
    comments_tuples = list(zip(comment_author_name, comment_text))

    if request.method == "POST" and "add_to_watchlist" in request.POST:
        watchlist_item = Watchlist(user_id=user_id, listing_id=listing_id)
        watchlist_item.save()
        user_watchlist = Watchlist.objects.get(user_id=request.user.id, listing_id=listing_id)  
        
        return HttpResponseRedirect(listing)

    elif request.method == "POST" and "delete_from_watchlist" in request.POST:
        watchlist_item= Watchlist.objects.get(user_id=user_id, listing_id=listing_id)
        watchlist_item.delete()
        user_watchlist = None
        return HttpResponseRedirect(listing)

    elif request.method == "POST" and "new_bid" in request.POST:
        new_bid = request.POST["new_bid"]
        Listing.objects.filter(id=listing_id).update(starting_bid=new_bid, highest_bid_id = user_id)
        return HttpResponseRedirect(listing)
    
    elif request.method == "POST" and "close_auction" in request.POST:
        Listing.objects.filter(id=listing_id).update(active=False)        
        return HttpResponseRedirect(listing)

    elif request.method == "POST" and "comment" in request.POST:
        comment_text = request.POST["comment"]
        comment = Comment(author_id=user_id, listing_id=listing_id, text = comment_text)
        comment.save()     
        return HttpResponseRedirect(listing)

    else:
        print(highest_bid_id, "highest_bid_id")
        return render(request, "auctions/listing.html", {
            "listing": ls,
            "watchlist": user_watchlist,
            "seller_id":seller_id,
            "user_id":user_id,
            "active": active,
            "highest_bid_id":highest_bid_id,
            "comments_tuples":comments_tuples,           
            })

def create_listing(request):
    if request.method == "POST":        
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        category = request.POST["category"]
        active = True
        
        highest_bid_id = 0
        current_user = request.user        
        seller_id = current_user.id

        listing = Listing(title=title, description=description, starting_bid=starting_bid, image_url=image_url, category=category, seller_id=seller_id, active=active,highest_bid_id=highest_bid_id )
        listing.save()
        
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html", {
        "categories": Categorie.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
