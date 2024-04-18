from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        app_label = 'quotes'

class LogoutForm(forms.Form):
    pass

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=100)
    quote_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def update_quote_count(self):
        self.quote_count = self.quotes.count()
        self.save()

class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='quotes')

    def __str__(self):
        return self.text[:50]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for tag in self.tags.all():
            tag.update_quote_count()

    def delete(self, *args, **kwargs):
        for tag in self.tags.all():
            tag.update_quote_count()
        super().delete(*args, **kwargs)