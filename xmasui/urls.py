from django.conf.urls import patterns, url

from xmasui import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
