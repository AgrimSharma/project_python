"""
Extra HTML Widget classes
"""

import datetime
import re

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.conf import settings


__all__ = ('SelectDateWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

class ReCaptcha(Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        return mark_safe(u'%s' % captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None), 
            data.get(self.recaptcha_response_name, None)]

class SelectDateWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, fromyear=-100, toyear=-10):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year + fromyear, this_year + toyear)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        month_choices.sort()
        month_choices.append(("","Month"))
        local_attrs = self.build_attrs(id=self.month_field % id_)
        month_html = Select(choices=month_choices).render(self.month_field % name, month_val, local_attrs)

        day_choices = [(i, i) for i in range(1, 32)]
        day_choices.append(('','Day'))
        local_attrs['id'] = self.day_field % id_
        day_html = Select(choices=day_choices).render(self.day_field % name, day_val, local_attrs)

        year_choices = [(i, i) for i in self.years]
        year_choices.append(("","Year"))
        local_attrs['id'] = self.year_field % id_
        year_html = Select(choices=year_choices).render(self.year_field % name, year_val, local_attrs)

        output.append(day_html)
        output.append(month_html)
        output.append(year_html)
        
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y, m, d = data.get(self.year_field % name), data.get(self.month_field % name), data.get(self.day_field % name)
        if y and m and d:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)
