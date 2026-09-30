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

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            'id',
            'home_no',
            'building_name',
            'street',
            'nearby_landmark',
            'zip_code',
            'type',
            'city',
            'state',
            'country',
            'is_default'
        ]

    def create(self, validated_data):
        user = self.context['request'].user

        if validated_data.get('is_default', False):
            user.addresses.filter(is_default=True).update(is_default=False)

        return Address.objects.create(
            customer=user,
            **validated_data
        )

    def update(self, instance, validated_data):
        if validated_data.get('is_default', False):
            instance.customer.addresses.filter(
                is_default=True
            ).exclude(
                id=instance.id
            ).update(is_default=False)

        return super().update(instance, validated_data)

    def validate_home_no(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError("Home number should be numeric")
        if len(value) > 4:
            raise serializers.ValidationError("Home number should be less then 5 digits")
        return value

    def validate_building_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Building name is required.")
        if value.isdigit():
            raise serializers.ValidationError("Building name should not be numeric")
        return value

    def validate_street(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Street is required."
            )
        return value

    def validate_nearby_landmark(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Nearby landmark is required."
            )
        return value

    def validate_zip_code(self, value):
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError(
                "ZIP code must contain only digits."
            )
        if len(value) not in [5, 6]:
            raise serializers.ValidationError(
                "ZIP code must contain 5 or 6 digits."
            )
        return value

    def validate_city(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "City is required."
            )
        return value

    def validate_state(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "State is required."
            )
        return value

    def validate_country(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Country is required."
            )
        return value

