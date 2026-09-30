import email

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User,Address

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8,required=True)
    first_name = serializers.CharField(required=True, allow_blank=False)
    email=serializers.CharField(required=True,allow_blank=False)
    class Meta:
        model = User
        fields=['email','phone','password','first_name','last_name']

    def validated_email(self,value):
        value=value.lower().strip()
        if email is None:
            raise serializers.ValidationError("Email is required")
        return value

    def validate_first_name(self,value):
        value=value.strip()
        if not value:
            raise serializers.ValidationError("The name is required.")
        return value

    def validate_password(self,value):
        validate_password(
            value,
            user=None
        )
        return  value
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True,allow_blank=False)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True
    )
    def validate(self,attr):
        email=attr.get('email')
        password=attr.get('password')
        if not email:
            raise serializers.ValidationError("Email is required.")

        if not password:
            raise serializers.ValidationError("Password is required")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Email or password is incorrect")

        user_token=RefreshToken.for_user(user)

        return {
            'email': user.email,
            'access_token': str(user_token.access_token),
            'refresh_token': str(user_token)
        }

