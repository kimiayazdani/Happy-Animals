from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, ChangePasswordSerializer, AccountPropertiesSerializer
from account_management.models import Account
from rest_framework.viewsets import ModelViewSet

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from django.contrib.auth import logout

import requests
import json


class AccountView(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )


class Logout(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        logout(request)
        data = {'Response': 'successful'}
        return Response(data)


@api_view(['POST', ])
@authentication_classes([])
def registration_view(request):
    data = {}
    email = request.data.get('email', '0').lower()
    if validate_email(email) != None:
        data['error_message'] = 'That email is already in use.'
        data['response'] = 'Error'
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    username = request.data.get('username', '0')
    if validate_username(username) != None:
        data['error_message'] = 'That username is already in use.'
        data['response'] = 'Error'
        return Response(data=data, status=status.HTTP_403_FORBIDDEN)
    password = request.data.get('password', '0')
    val = validate_password(password)
    if val[0] == None:
        data['error_message'] = val[1]
        data['response'] = 'Error'
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    serializer = RegistrationSerializer(data=request.data)

    if serializer.is_valid():
        account = serializer.save()
        account.save()
        ser = RegistrationSerializer(account)
        data = ser.data
        Token.objects.create(user=account)
        data['userId'] = account.pk
        data['profilePicture'] = account.avatar.url
        data['email'] = account.email
        data['username'] = account.username
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data = serializer.errors

        return Response(data=data, status=status.HTTP_403_FORBIDDEN)


def validate_email(email):
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return None
    if account != None:
        return email


def validate_username(username):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return None
    if account != None:
        return username


def validate_password(passwd):
    SpecialSym = ['$', '@', '#', '%']
    val = {0: "not None", 1: "not any error"}

    if len(passwd) < 6:
        val[0] = None
        val[1] = 'password is too short!'
        return val
    if len(passwd) > 40:
        val[0] = None
        val[1] = 'Password is too long!!'
        return val
    if not any(char.isdigit() for char in passwd):
        val[0] = None
        val[1] = 'your password must contain at least one digit.'
        return val
    if not any(char.isupper() for char in passwd):
        val[0] = None
        val[1] = 'your password must contain at least one uppercase alphabet.'
        return val
    if not any(char.islower() for char in passwd):
        val[0] = None
        val[1] = 'your password must contain at least one lowercase alphabet.'
        return val

    if any(char in SpecialSym for char in passwd):
        val[0] = None
        val[1] = 'your passwrod shouldn\'t contain any of {@,#,%,$ } set'
        return val
    return val


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def account_properties_view(request):
    try:
        account = request.user
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountPropertiesSerializer(account)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', ])
@permission_classes((IsAuthenticated,))
@authentication_classes((TokenAuthentication, ))
def update_account_view(request):
    try:
        account = request.user
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = AccountPropertiesSerializer(account, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = 'Account update success'
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {}
        email = request.POST.get('username')
        password = request.POST.get('password')
        account = authenticate(email=email, password=password)
        if account:
            context['response'] = 'Successfully authenticated.'
            context['pk'] = account.pk
            context['email'] = email.lower()
            context['image'] = str(account.avatar)
            return Response(data=context, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([])
def does_account_exist_view(request):
    if request.method == 'GET':
        email = request.GET['email'].lower()
        data = {}
        try:
            account = Account.objects.get(email=email)
            data['response'] = email
        except Account.DoesNotExist:
            data['response'] = "Account does not exist"
            return Response(data=data, status=status.HTTP_403_FORBIDDEN)
        return Response(data, status=status.HTTP_501_NOT_IMPLEMENTED)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = Account
    permission_classes = (IsAuthenticated,)

    authentication_classes = (TokenAuthentication,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # confirm the new passwords match
            new_password = serializer.data.get("new_password")
            confirm_new_password = serializer.data.get("confirm_new_password")
            if new_password != confirm_new_password:
                return Response({"new_password": ["New passwords must match"]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"response": "successfully changed password"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
