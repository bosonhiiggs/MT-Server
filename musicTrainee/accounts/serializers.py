from rest_framework import serializers

from accounts.models import CustomAccount


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAccount
        fields = ['id', 'username', 'email', 'avatar', 'is_moderator']
