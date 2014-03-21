from rest_framework import serializers
from applications.models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    creator = serializers.Field(source='created_by.username')
    key = serializers.Field(source='key')
    secret = serializers.Field(source='secret')

    class Meta:
        model = Application
        fields = ('name', 'key', 'secret', 'creator', 'created_on', 'modified_on')