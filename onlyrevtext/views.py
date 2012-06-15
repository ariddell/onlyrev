from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from onlyrevtext.models import Line, Location, Page

def line_list(request, character, page):
    lines = Line.objects.filter(section="main",character=character,page=page).order_by('character','page','line')
    sidebar_list = Line.objects.filter(section="sidebar",character=character,page=page).order_by('character','page','line')
    # now pair each line with a sidebar line -- while allowing
    # for the special case where sidebar_list is empty.
    if len(sidebar_list) > len(lines):
        length_difference = len(sidebar_list) - len(lines)
        lines = [l for l in lines] + [None]*length_difference
    else:
        length_difference = abs(len(lines) - len(sidebar_list))
        sidebar_list = [s for s in sidebar_list] + [None]*length_difference
    paired_lines = zip(lines,sidebar_list) # would use itertools.izip_longest but that's only in 2.6+
    page_obj, created = Page.objects.get_or_create(character=character, page=page)
    info_dict = {"object_list" : lines,
                 "character": character,
                 "page": int(page),
                 "page_obj": page_obj,
                 "sidebar_list": sidebar_list,
                 "paired_lines": paired_lines,
                 "types" : Line.objects.filter(section="main",character=character,page=page).exclude(type=""),
                 "locations": Location.objects.filter(line__in=lines),
                 }
    page = int(page)
    if page < 365:
        info_dict.update({"nextpage": page + 1})
    if page > 1:
        info_dict.update({"prevpage": page - 1})
    template = "onlyrevtext/line_list.html"
    return render_to_response(template, info_dict, context_instance=RequestContext(request))

def raw_text(request):
    lines = Line.objects.filter(section="main").order_by('character','page','line')
    text = '\n'.join([line.text for line in lines])
    import re
    p = re.compile(r'<.*?>') # strip html tags
    text = p.sub('', text)
    p = re.compile(r' +') # remove duplicate whitespace
    text = p.sub(' ', text)
    return HttpResponse("<html><body><pre>"+ text +"</pre></body></html>")

def page_list(request,section=None,character=None):

    if section and character:
        lines = Line.objects.filter(section=section,
                                    character=character).values('character', 'page').distinct()
    elif section:
        lines = Line.objects.filter(section=section).values('character','page').distinct()
    else:
        lines = Line.objects.values('character','page').distinct()
    template = "onlyrevtext/page_list.html"
    return render_to_response(template,
                              {'object_list': lines,},
                              context_instance=RequestContext(request))

def search(request):
    template = "onlyrevtext/search.html"
    results = None
    q = None
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        results = Line.objects.filter(text__icontains=q)
    return render_to_response(template,
                              {'results': results, 'query': q},
                              context_instance=RequestContext(request))

def category_list(request, category):
    """
    Cars, plants, animals, minerals etc. Right now restrict display of plant
    and animal types to those that are boldfaced.
    """
    if category == "animal" or category == "plant":
        lines = Line.objects.filter(section="main",
                                    type__contains=category,
                                    text__contains="b>").order_by('character','page','line')
    else:
        lines = Line.objects.filter(section="main",
                                    type__contains=category).order_by('character','page','line')
    template = "onlyrevtext/category_list.html"
    return render_to_response(template,
                              {'category': category,
                               'object_list': lines, },
                              context_instance=RequestContext(request))

# map-related views

def location_list(request):
    locations = Location.objects.all().order_by('line__character',
                                                'line__page',
                                                'line__line',
                                                'linepos')
    template = "onlyrevtext/location_list.html"
    return render_to_response(template, {'locations': locations},
                              context_instance=RequestContext(request))

def location_map(request):
    """
    NB: must pass domain as google map api requires communication back and
    forth between google api and website.
    """
    template = "onlyrevtext/map.html"
    try:
        apikey = settings.GOOGLE_MAPS_API_KEY
    except NameError:
        raise ImproperlyConfigured("Set GOOGLE_MAPS_API_KEY in settings.py for map view.")
    try:
        domain = Site.objects.get_current().domain
    except ImproperlyConfigured: # for testing without Site framework
        domain = "http://localhost:8000"
    return render_to_response(template,
                              { 'domain': domain,
                                'apikey': apikey },
                              context_instance=RequestContext(request))

def location_kml(request):
    kml = ""
    if 'char' in request.GET and request.GET['char'] == 'S':
        char = "S"
        locs = Location.objects.filter(line__character='S').order_by('line__page',
                                                                     'line__line',
                                                                     'linepos')
    elif 'char' in request.GET and request.GET['char'] == 'H':
        char = "H"
        locs = Location.objects.filter(line__character='H').order_by('line__page',
                                                                     'line__line',
                                                                     'linepos')
    else:
        raise Http404
    if 'type' in request.GET and request.GET['type'] == "path":
        if char == "S":
            title = _(u"Sam's Path")
        elif char == "H":
            title = _(u"Hailey's Path")
        kml += _line_kml(locs)
    else:
        raise Http404
    template = "onlyrevtext/kml_wrapper.kml"
    return render_to_response(template, { 'title': title, 'kml': kml },
                              mimetype='application/vnd.google-earth.kml+xml')

def _placemark_kml(location):
    t = loader.get_template("onlyrevtext/snippets/placemark.kml")
    c = Context({ 'location': location })
    kml_snippet = t.render(c)
    return kml_snippet

def _line_kml(locations):
    """Assume locations are in the desired order, i.e. from first to last."""
    t = loader.get_template("onlyrevtext/snippets/line.kml")
    c = Context({ 'location_pairs': zip(locations, locations[1:]) })
    kml_snippet = t.render(c)
    return kml_snippet
