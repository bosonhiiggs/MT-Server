from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import CustomAccount, PasswordResetRequest


class ProfileInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели для просмотра информации о пользователе.
    """
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomAccount
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar', 'is_activated', 'is_moderator']

    def get_avatar(self, obj):
        request = self.context.get('request')
        url = obj.avatar.url
        if request:
            host: str = request.get_host()
            port: str = request.get_port()
            if settings.IS_DEV_SERVER:
                if host.endswith(f':{port}'):
                    host = host[:-len(f':{port}')]
                return f'http://{host}:{port}{url}'
            else:
                return f'http://{host}:{port}{url}'

        return url



class ProfileLoginSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели для входа пользователя.
    """
    class Meta:
        model = CustomAccount
        fields = ['username', 'password']


class ProfileCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели для создания пользователя.
    """
    # email = serializers.EmailField(required=False)

    class Meta:
        model = CustomAccount
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        if CustomAccount.objects.filter(email=value).exists():
            raise ValidationError("This email is already in use.")
        return value


class ProfileConfirmSerializer(serializers.Serializer):
    confirm_code = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Сериализатор подтверждения почты для сброса пароля.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        # Проверка адреса электронной почты
        if not CustomAccount.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("No user found with this email")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения пароля
    """
    reset_code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


# class UserPatchSerializer(serializers.Serializer):
#     first_name = serializers.CharField(required=False)
#     last_name = serializers.CharField(required=False)
#     email = serializers.EmailField(required=False)
#     avatar = serializers.ImageField(required=False)
#     is_moderator = serializers.BooleanField(required=False)
#

class UserPatchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAccount
        fields = ['first_name', 'last_name', 'email', 'avatar', 'is_moderator']

        # def update(self, instance, validated_data):
        #     for attr, value in validated_data.items():
        #         setattr(instance, attr, value)
        #
        #     if 'avatar' in validated_data:
        #         old_avatar = instance.avatar
        #         if old_avatar and old_avatar != instance.default_avatar:
        #             old_avatar.delete(save=False)
        #
        #     instance.save()
        #     return instance
