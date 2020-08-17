from django.db import models
import uuid
# Create your models here.

class user(models.Model):
    uuid = models.AutoField(primary_key=True)
    username = models.CharField( blank=False, max_length=255)
    password = models.CharField( blank=False, max_length=255) 

    def __str__(self):
        return self.username

class collection(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(user, on_delete = models.CASCADE) 
    title = models.CharField( blank=False, max_length=255)
    description = models.CharField( blank=False, max_length=255)

    def __str__(self):
        return self.title

class movie(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    collection_id = models.ForeignKey(collection, on_delete = models.CASCADE)
    title = models.CharField( blank=False, max_length=255)
    description = models.CharField( blank=False, max_length=255)
    genres = models.CharField( blank=False, max_length=255)

    def __str__(self):
        return self.title
