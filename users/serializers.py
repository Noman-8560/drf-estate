from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, Properties


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate_password(self, value):
        data = self.get_initial()
        password = data.get('password2')
        password2 = value
        if password != password2:
            raise ValidationError('Passwords must match')
        return value

    def validate_password2(self, value):
        data = self.get_initial()
        password = data.get('password')
        password2 = value
        if password != password2:
            raise ValidationError('Passwords must match')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class PropertiesSerializer (serializers.ModelSerializer):

    class Meta:
        model = Properties
        fields = "__all__"