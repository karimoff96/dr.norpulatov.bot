from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from bot import signals, views

urlpatterns = [
    path('bot/index/', views.index, name='handler'),
    path('bot/cron/', signals.cron_job),
    path('bot/clear/', signals.clear_appointment),
    path('bot/rosetta/', include('rosetta.urls')),
    path('bot/send/', views.send_process),
]
if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

urlpatterns += [path('', admin.site.urls)]