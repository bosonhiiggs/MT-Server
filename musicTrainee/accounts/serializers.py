from rest_framework import serializers

from accounts.models import CustomAccount


class ProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAccount
        fields = ['id', 'username', 'avatar', 'is_moderator']


class ProfileLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAccount
        fields = ['username', 'password']


class ProfileCreateSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=False)

    class Meta:
        model = CustomAccount
        fields = ['username', 'email', 'password']
