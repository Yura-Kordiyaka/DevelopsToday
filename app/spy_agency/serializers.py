from rest_framework import serializers
from .models import CustomUser


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', "email", 'password')
        write_only_fields = ('password',)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

