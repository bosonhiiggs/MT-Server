from rest_framework import serializers

from accounts.models import CustomAccount


class ProfileInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели для просмотра информации о пользователе.
    """
    class Meta:
        model = CustomAccount
        fields = ['id', 'username', 'avatar', 'is_moderator']


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



