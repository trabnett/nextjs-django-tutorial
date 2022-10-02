from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.hashers import make_password

from .serializers import SignUpSerializer, UserSerializer

from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User

# Create your views here.

@api_view(['POST'])
def register(request):
  data = request.data

  user = SignUpSerializer(data=data)
  if user.is_valid():
    if not User.objects.filter(username=data['email']).exists():
      user = User.objects.create(
        first_name = data.get('first_name'),
        last_name = data.get('last_name'),
        username = data.get('email'),
        email = data.get('email'),
        password = make_password(data['password'])
      )
      return Response({
        'message': 'User registered'},
        status=status.HTTP_200_OK,
      )
    else:
      return Response({
        'error': 'User already exists'},
        status=status.HTTP_400_BAD_REQUEST,
      )

  else:
    return Response(user.errors)

def go(request):
  return Response({'hey': 'you'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
  user = request.user

  serializer = UserSerializer(user, many=False)

  return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
  user = request.user

  serializer = UserSerializer(user, many=False)

  data = request.data

  user.first_name = data.get('first_name') or user.first_name
  user.last_name = data.get('last_name') or user.last_name
  user.username = data.get('last_name') or user.username
  user.email = data.get('email') or user.email

  if data.get('password') and data['password'] != '':
    user.password = make_password(data['password'])

  user.save()

  user = UserSerializer(user, many=False)
  return Response(serializer.data)


