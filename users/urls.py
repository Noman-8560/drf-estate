from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, PropertiesListAV, PropertiesDetailAV, StripeCheckoutView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('list/', PropertiesListAV.as_view(), name='propertie_list'),
    path('<int:pk>', PropertiesDetailAV.as_view(), name='propertie_details'),
    path('create-checkout-session', StripeCheckoutView.as_view()),

]