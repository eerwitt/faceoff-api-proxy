import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from applications import application_cache
from faceoff.models import FaceoffModel


class Application(FaceoffModel):
    json_fields = ['name', 'id', 'super_application', 'created_by']

    name = models.CharField(max_length=100)
    client_secret = models.CharField(max_length=32)
    super_application = models.BooleanField(default=False)
    created_by = models.CharField(max_length=36)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    redirect_uri = models.URLField()

    def __unicode__(self):
        return self.name

    @staticmethod
    def create_application(name, created_by, redirect_uri, super_application=False):
        a = Application()
        a.name = name
        a.client_secret = uuid.uuid4().hex
        a.super_application = super_application
        a.created_by = created_by.id
        a.redirect_uri = redirect_uri
        a.save()
        return a


@receiver(post_save, sender=Application)
def update_application_cache(sender, **kwargs):
    application_cache().load_from_db()
