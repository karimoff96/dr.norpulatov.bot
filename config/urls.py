from django.contrib import admin
from django.urls import include, path
from django.conf import settings 
from django.conf.urls.static import static 

from bot import views

urlpatterns = [
    path('bot/', views.index, name='handler'),
    path('cron/', views.cron_job),
    path('rosetta/', include('rosetta.urls')),
]
if settings.DEBUG:
    urlpatterns += static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

urlpatterns += [path('', admin.site.urls)]