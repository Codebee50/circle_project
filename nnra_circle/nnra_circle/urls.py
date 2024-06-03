from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('circle.urls', namespace='circle')), 
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('memo/', include("memo.urls", namespace='memo'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)