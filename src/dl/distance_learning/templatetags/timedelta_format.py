from django import template

register = template.Library()

@register.filter(expects_localtime=True)
def timedelta_format(value):
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
