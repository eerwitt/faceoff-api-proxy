import json
from django.db import models
from django_extensions.db.fields import UUIDField


class FaceoffModel(models.Model):
    json_fields = []

    id = UUIDField(primary_key=True)

    class Meta:
        abstract = True

    def to_json(self):
        json_dict = dict()
        for x in self.json_fields:
            json_dict[x] = getattr(self, x)
        return json.dumps(json_dict)