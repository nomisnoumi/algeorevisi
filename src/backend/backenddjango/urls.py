from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # Tambahkan ini untuk melayani file media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('simsalabim/', include('simsalabim.urls')),  # Include simsalabim app URLs
    path('api/', include('rest_framework.urls')),  # Optional: if using Django REST framework
]

# Tambahkan ini untuk melayani file media saat DEBUG = True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)