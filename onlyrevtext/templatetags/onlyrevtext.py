"""
Template tags for nicely displaying lines of the Only Revolutions text.

Example::

    {% load onlyrevtext %}
    <ul>
    {% for line in lines %}
        <li>
        {% render_line line %}
        </li>
    {% endfor %}
    </ul>
"""

from django import template

register = template.Library()

@register.inclusion_tag('onlyrevtext/snippets/line_snippet.html')
def render_line(line):
    return {'line': line}
