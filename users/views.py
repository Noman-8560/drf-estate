from django.http import HttpResponse
import stripe
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, PropertiesSerializer
from .models import User, Properties, PaymentHistory
from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import jwt
import datetime
from django.conf import settings


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


API_URL = "http/locahost:8000"


class ProductPreview(RetrieveAPIView):
    serializer_class = PropertiesSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Properties.objects.all()


class CreateCheckOutSession(APIView):
    def post(self, request, *args, **kwargs):
        prod_id = self.kwargs["pk"]
        try:
            Propertie = Properties.objects.get(id=prod_id)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(Propertie.price) * 100,
                            'product_data': {
                                'name': Propertie.name,
                                'images': [f"{API_URL}/{Propertie.images}"]

                            }
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    "product_id": Propertie.id
                },
                mode='payment',
                success_url=settings.SITE_URL + '?success=true',
                cancel_url=settings.SITE_URL + '?canceled=true',
            )
            return redirect(checkout_session.url)
        except Exception as e:
            return Response({'msg': 'something went wrong while creating stripe session', 'error': str(e)}, status=500)


# custom payment flow
class CreatePaymentIntent(APIView):
    def post(self, request, *args, **kwargs):
        prod_id = request.data
        Propertie = Properties.objects.get(id=prod_id)
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(Propertie.price) * 100,
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    'product_id': Propertie.id
                }
            )
            return Response({'clientSecret': intent['client_secret']}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=400)


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_SECRET_WEBHOOK
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']

        print(intent)
        payment_intent = intent.charges.data[0]
        # customer_email=session['customer_details']['email']
        prod_id = payment_intent['metadata']['product_id']
        Propertie = Properties.objects.get(id=prod_id)

        # #creating payment history
        # # user=User.objects.get(email=customer_email) or None

        PaymentHistory.objects.create(product=Propertie, payment_status=True)
    # Passed signature verification
    return HttpResponse(status=200)


# class PropertiesListAV(APIView):
#
#     def get(self, request):
#         Propertie = Properties.objects.all()
#         serializer = PropertiesSerializer(Propertie, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = PropertiesSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)
#



























#
# class PropertiesListAV(APIView):
#
#     def get(self, request):
#         Propertie = Properties.objects.all()
#         serializer = PropertiesSerializer(Propertie, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = PropertiesSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)
#
#
# class PropertiesDetailAV(APIView):
#
#     def get(self, request, pk):
#         try:
#             Propertie = Properties.objects.get(pk=pk)
#         except Properties.DoesNotExist:
#             return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = PropertiesSerializer(Propertie)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         Propertie = Properties.objects.get(pk=pk)
#         serializer = PropertiesSerializer(Propertie, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         Propertie = Properties.objects.get(pk=pk)
#         Propertie.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
