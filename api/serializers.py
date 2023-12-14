from rest_framework import serializers
from .models import Content

class ContentSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)


class add_contents_serializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    genre = serializers.ListField(required=False) 
    description = serializers.CharField(required=False) 
    age_rating=serializers.ListField(required=False)
    release_date = serializers.DateField(required=True)
    duration = serializers.DurationField(required=True)
    rating = serializers.DecimalField(max_digits=2,decimal_places=1)
    location=serializers.ListField(required=False)
    director=serializers.ListField(required=False)
    producer=serializers.ListField(required=False)
    cast=serializers.ListField(required=False)
    actor=serializers.ListField(required=False)
    actress=serializers.ListField(required=False)
    is_trending=serializers.BooleanField(required=False,default=True)
    thumbnail = serializers.ImageField(required=True)
   
    # subtitlelanguages=serializers.ListField(required=False)