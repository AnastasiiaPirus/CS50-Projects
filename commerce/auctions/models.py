from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass



class Categorie(models.Model):
    category_name = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.category_name}"
    

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=5000)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=5000)
    category = models.CharField(max_length=5000) #check after adding categories
    seller_id =  models.IntegerField()
    active = models.BooleanField()
    highest_bid_id = models.IntegerField()

    def __str__(self):
            return f"{self.id}) {self.title}: {self.description}"

class Watchlist(models.Model):
    user_id = models.IntegerField()
    listing_id=models.IntegerField()

class Comment(models.Model):
    author_id = models.IntegerField()
    listing_id=models.IntegerField()
    text = models.CharField(max_length=5000)