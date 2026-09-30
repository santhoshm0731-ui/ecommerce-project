from itertools import accumulate

from .models import Address
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer,LoginSerializer,AddressSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        user = serializer.save()
        return Response(
            {
                "message": "Registered successfully",
                "id": user.id,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer=LoginSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        data=serializer.validated_data
        return Response(
            {
                'message': "Logged in Successfully.",
                'access': data['access_token'],
                'refresh': data['refresh_token']
            },
           status=status.HTTP_200_OK
        )

class Meview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user=request.user
        return Response(
            {
                'message': "Here is your details.",
                'name':user.first_name+" "+user.last_name,
                'email': user.email,
                'phone': user.phone
            },
            status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        refresh_token=request.data.get('refresh')
        token=RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {
                'message':"Logged out successfully."
            },
            status=status.HTTP_200_OK
        )

