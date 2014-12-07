from django.conf.urls import patterns, url

from xmasui import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^setProgram$', views.setProgram, name='setProgram'),
    url(r'^setFPS$', views.setFPS, name='setFPS'),
    url(r'^setPower$', views.setPower, name='setPower'),
    url(r'^setPreprogrammed$', views.setPreprogrammed, name='setPreprogrammed'),
    url(r'^getSettings$', views.getSettings, name='getSettings'),
)
