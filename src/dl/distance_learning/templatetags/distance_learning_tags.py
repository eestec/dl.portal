import re
from django import template

register = template.Library()

@register.filter(expects_localtime=True)
def timedelta_format(value):
    """
    A filter which returns a human-readable representation of a timedelta
    object.
    """
    try:
        total = value.days * 24 * 60 * 60 + value.seconds
        minutes = total // 60
        hours = minutes // 60
        days = hours // 24
        if days > 0:
            return '{0} day{1}'.format(days, 's' if days > 1 else '')
        elif hours > 0:
            return '{0} hour{1}'.format(hours, 's' if hours > 1 else '')
        elif minutes > 0:
            return '{0} minute{1}'.format(minutes, 's' if minutes > 1 else '')
        else:
            return '{0} second{1}'.format(total,
                                          ('s' if total > 1 or total == 0 else
                                           ''))
    except:
        return ''

@register.filter
def link_urls(value):
    """
    The filter finds all substrings which represent URLs and wrap them in HTML
    <a> tags.
    When used in a template, the resulting value needs to be marked as safe.
    """
    regexp = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    regexp = (
        """http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|"""
        """(?:%[0-9a-fA-F][0-9a-fA-F]))+"""
    )

    parts = []
    last = 0
    try:
        for m in re.finditer(regexp, value):
            parts.append(value[last:m.start()])
            parts.append('<a href="' + m.group() + '">' + m.group() + '</a>')
            last = m.end()
        return ''.join(parts)
    except:
        return value

