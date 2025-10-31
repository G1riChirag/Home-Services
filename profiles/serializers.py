from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "name",
            "age",
            "language",
            "citizenship",
            "covid_status",
            "consent",
            "address",
        )
