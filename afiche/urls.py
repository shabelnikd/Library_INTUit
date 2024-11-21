from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter

from event.views import BookViewSet, NewsViewSet, DirectionStatsViewSet

router = DefaultRouter()
router.register('', BookViewSet)

news = DefaultRouter()
news.register('', NewsViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('account.urls')),
    path('api/v1/books/', include(router.urls)),
    path('api/v1/news/', include(router.urls)),
    path('api/v1/stats/', DirectionStatsViewSet.as_view({'get': 'list'}), name='stats'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
