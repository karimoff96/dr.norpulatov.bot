from django.contrib import admin
from django.urls import include, path
from django.conf import settings 
from django.conf.urls.static import static 

from bot import views, signals

urlpatterns = [
    path('bot/', views.index, name='handler'),
    path('cron/', signals.cron_job),
    path('clear/', signals.clear_appointment),
    path('rosetta/', include('rosetta.urls')),
]
if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

urlpatterns += [path('', admin.site.urls)]