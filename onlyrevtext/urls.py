from django.conf.urls.defaults import *

urlpatterns = patterns('onlyrevtext.views',
    url(r'^(?P<character>(H|S))/(?P<page>\d+)/$', 'line_list', name="onlyrevtext_line_list"),
    url(r'^(?P<character>(H|S))/$', 'page_list', name="onlyrevtext_page_list"),
    url(r'^$', 'page_list', {"section": "main"}, name="onlyrevtext_index"), # index for now
    url(r'^raw/$','raw_text'),
    url(r'^category/(car|animal|plant|mineral)/$','category_list', name="onlyrevtext_category_list"),
    url(r'^search/$', 'search', name="onlyrevtext_search"),
    url(r'^location/$', 'location_list', name="onlyrevtext_location_list"),
    url(r'^location/map/$','location_map',name="onlyrevtext_location_map"),
    url(r'^location/kml/$','location_kml', name="onlyrevtext_location_kml"),
)
