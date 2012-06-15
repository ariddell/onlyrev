from django.db import models

SECTION_CHOICES = (("main","Main Text"),
                   ("sidebar","Chronology (sidebar)"))
CHARACTER_CHOICES = (("S","Sam"), ("H","Hailey"))

class LineManager(models.Manager):
    def get_by_natural_key(self, section, character, page, line):
        return self.get(section=section,
                        character=character,
                        page=page,
                        line=line)

class Line(models.Model):
    """Lines from the novel *Only Revolutions*."""
    objects = LineManager()
    section = models.CharField(max_length=8, choices=SECTION_CHOICES)
    character = models.CharField(max_length=1) # S = Sam or H = Hailey
    page = models.PositiveSmallIntegerField()
    date = models.DateField()
    line = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=200)
    type = models.CharField(max_length=100, blank=True)
    type_text = models.CharField(max_length=100, blank=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def natural_key(self):
        return (self.section, self.character, self.page, self.line)

    @property
    def character_full(self):
        return dict(CHARACTER_CHOICES)[self.character]

    @models.permalink
    def get_absolute_url(self):
        return ('onlyrevtext_line_list', (), {'character': self.character, 'page': self.page})

    def __unicode__(self):
        if self.section == "main":
            return "%s/%s/%s %s" % (self.character, self.page, self.line, self.text)
        else:
            return "(%s) %s/%s/%s %s" % (self.section, self.character,
                                         self.page, self.line, self.text)

    class Meta:
        ordering = ['section', 'character', 'page', 'line']
        unique_together = [('section', 'character', 'page', 'line')]

class Page(models.Model):
    """Dummy model to provide a place for page-level comments."""
    character = models.CharField(max_length=1)
    page = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return "Page %s/%s" % (self.character, self.page)

    class Meta:
        ordering = ['character', 'page']
        unique_together = [('character', 'page')]

class Location(models.Model):
    """Locations mentioned in *Only Revolutions*."""
    line = models.ForeignKey(Line)
    linepos = models.IntegerField(max_length=2,
                                  help_text="Position of word in the line.")
    words = models.CharField(max_length=255,
                             help_text="Word(s) in text. i.e. 'Union'")
    words_annotated = models.CharField(max_length=1000,blank=True,
                           help_text="Inferred location name." +
                                     "i.e. 'Union Station'")
    geonames_name = models.CharField(max_length=1000,blank=True,null=True)
    geonames_state = models.CharField(max_length=1000,blank=True,null=True)
    geonames_fcodename = models.CharField(max_length=1000,blank=True,null=True)
    geonames_id = models.PositiveIntegerField(blank=True,null=True)
    lat = models.FloatField(blank=True,null=True)
    lng = models.FloatField(blank=True,null=True)
    flagged = models.BooleanField(help_text="Uncertain of position?")
    # Automatic fields
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @models.permalink
    def get_absolute_url(self):
        return ('onlyrevtext_location_list', (), {})

    def __unicode__(self):
        if self.words_annotated:
            return "%s (%s) %s" % (self.words,self.words_annotated, self.line)
        else:
            return "%s %s" % (self.words,self.line)

    class Meta:
        ordering = ['line', 'linepos']
        unique_together = [('line', 'words')]
