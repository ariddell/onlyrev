# project urls
from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {'template': 'homepage.html'}, name='home'),
    url(r'^text/', include('onlyrevtext.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^poster/$', direct_to_template, {'template': 'poster.html'}, name='poster'),
    url(r'^endpapers$', direct_to_template, {'template': 'endpapers.html'}, name='endpapers'),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns += staticfiles_urlpatterns()
