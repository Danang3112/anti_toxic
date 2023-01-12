from django.urls import path,re_path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('audio',views.Audio_store, name='Audio_store'),
    path('', views.index, name='index'),
    path('tampil/', views.tampil, name='tampil'),
    path('kamus/', views.kamus, name='kamus'),
    path('rekaps/', views.rekaps, name='rekaps'),
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)