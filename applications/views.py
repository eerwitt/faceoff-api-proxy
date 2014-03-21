from rest_framework import generics
from applications.models import Application
from applications.serializers import ApplicationSerializer


class ApplicationList(generics.ListCreateAPIView):
    model = Application
    serializer_class = ApplicationSerializer


class ApplicationDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Application
    serializer_class = ApplicationSerializer

