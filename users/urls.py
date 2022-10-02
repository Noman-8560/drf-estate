from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, ProductPreview, CreatePaymentIntent, CreateCheckOutSession, stripe_webhook_view
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('list/<int:pk>/', ProductPreview.as_view(), name='product'),
    path('webhook/', stripe_webhook_view, name='stripe-webhook'),
    path('create-checkout-session/<pk>/', csrf_exempt(CreateCheckOutSession.as_view()), name='checkout_session'),
    path('create-payment-intent/', CreatePaymentIntent.as_view(), name='payment-intent')
]
