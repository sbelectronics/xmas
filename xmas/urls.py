from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'xmas.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^xmas/', include('xmasui.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
