from rest_framework import serializers
from . import models


class DucumentsSerializers(serializers.ModelSerializer):
    def meta(self):
        model = models.Documents
        fields = "__all__"
