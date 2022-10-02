from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

route = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/stripe/', include('users.urls'))
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
