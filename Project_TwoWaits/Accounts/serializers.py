from .models import UserAccount
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

class AccountSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

# class LoginUserSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(max_length=128, write_only=True)
