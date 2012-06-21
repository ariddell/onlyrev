from django.test import TestCase
from django import template
from django.core.urlresolvers import reverse
from onlyrevtext.models import Line, Location

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class ClientTests(TestCase):

    fixtures = ["test-lines.json", "test-locations.json"] # pages 129 to 150

    def test_index(self):
        response = self.client.get(reverse('onlyrevtext_index'))
        self.failUnlessEqual(response.status_code, 200)

    def test_line_list_view(self):
        l = Line.objects.get(character="H", section="main", page=129, line=1)
        response = self.client.get(l.get_absolute_url())
        self.failUnlessEqual(response.status_code, 200)

class ClientTestsTestmaker(TestCase):

    def test_testmaker_urls(self):
        responses = [
            self.client.get(reverse('onlyrevtext_location_map')),
            self.client.get(reverse('onlyrevtext_location_map'),
                            {'char': "S", 'type': "path"}),
            self.client.get(reverse('onlyrevtext_location_map'),
                            {'char': "H", 'type': "path"}),
            self.client.get(reverse('onlyrevtext_category_list', args=['animal'])),
            self.client.get(reverse('onlyrevtext_search'), {'q': 'creep'})
        ]
        for r in responses:
            self.assertEqual(r.status_code, 200)

class ModelTests(TestCase):

    fixtures = ["test-lines.json", "test-locations.json"] # pages 129 to 150

    def testLine(self):
        l = Line.objects.get(character="H", section="main", page=129, line=1)
        self.assertEqual(l.text, u"<b>A</b>sphalt amped and jamming,")

    def testLocation(self):
        l = Line.objects.get(character="H", section="main", page=129, line=8)
        locs = Location.objects.filter(line=l)
        self.assertEqual(len(locs), 2)
        locs = Location.objects.filter(line=l).order_by('linepos')
        self.assertEqual(locs[0].words,u"Rolling Fork")
        self.assertEqual(locs[1].words,u"Hollywood")

class TagTestCase(TestCase):
    """Helper class with some tag helper functions"""

    def installTagLibrary(self, library):
        template.libraries[library] = __import__(library)

    def renderTemplate(self, tstr, **context):
        t = template.Template(tstr)
        c = template.Context(context)
        return t.render(c)

class RenderTagTest(TagTestCase):

    fixtures = ["test-lines.json", "test-locations.json"] # pages 129 to 150

    def setUp(self):
        self.installTagLibrary('onlyrevtext.templatetags.onlyrevtext')

    def testRenderSimple(self):
        l = Line.objects.get(character="H", section="main", page=129, line=1)
        o = self.renderTemplate("{% load onlyrevtext %}{% render_line l %}", l=l)
        self.assert_(o.startswith(u'\n<span class="onlyrevtext-line">'), o)
