from django.db import models
from django.conf import settings


class Tag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(Ingredient)

    def __str__(self):
        return self.title
