from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, PropertiesSerializer
from .models import User, Properties
import jwt
import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


class PropertiesListAV(APIView):

    def get(self, request):
        Propertie = Properties.objects.all()
        serializer = PropertiesSerializer(Propertie, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PropertiesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PropertiesDetailAV(APIView):

    def get(self, request, pk):
        try:
            Propertie = Properties.objects.get(pk=pk)
        except Properties.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PropertiesSerializer(Propertie)
        return Response(serializer.data)

    def put(self, request, pk):
        Propertie = Properties.objects.get(pk=pk)
        serializer = PropertiesSerializer(Propertie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        Propertie = Properties.objects.get(pk=pk)
        Propertie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StripeCheckoutView(APIView):
    def post(self, request):
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': 'price_1LoZt4Di64lensrv4CwzBKx8',
                        'quantity': 1,
                    },
                ],
                payment_method_types=['card'],
                mode='payment',
                success_url=settings.SITE_URL + '/?success=true&session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.SITE_URL + '/?canceled=true',
            )

            return redirect(checkout_session.url)
        except:
            return Response(
                {'error': 'Something went wrong when creating stripe checkout session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
