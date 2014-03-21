from django_extensions.db.fields import UUIDField
from applications.models import Application
from django.db import models
from faceoff.models import FaceoffModel


class AccessToken(FaceoffModel):
    user = models.CharField(max_length=128)  # this maps to a UUID in some other system
    token = UUIDField()
    application = models.ForeignKey(Application)
    created_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.token
