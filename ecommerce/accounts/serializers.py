from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from accounts.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8,required=True)
    class Meta:
        model = User
        fields=['email','phone','password','first_name','last_name']

    def validate_password(self,value):

        validate_password(
            value,
            user=None
        )
        return  value
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password = serializers.CharField(write_only=True,min_length=8,required=True)

    # def validate(self,data):
    #     email=data.get('email')
    #     password=data.get('password')
    #
    #     if not email or not password:
    #         raise serializers.ValidationError({'email':'Email or Password is required'})
    #     else:
    #         user=authenticate(email=email,password=password)
    #         if not user:
    #             raise serializers.ValidationError({'email':'Email or Password is invalid'})
    #         else:
    #             data['user']=user
    #             return data