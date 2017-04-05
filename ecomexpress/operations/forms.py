from django import forms

from service_centre.models import Bags
from .models import ConsolidatedBag


class ConsolidateBagForm(forms.ModelForm):

    class Meta:
        model = ConsolidatedBag
        fields = ('bag_number', 'hub', 'destination')

    # need to add to checks for validating bag number.
    def clean_bag_number(self):
        bag_number = self.cleaned_data.get('bag_number')
        try:
            Bags.objects.get(bag_number=bag_number)
            raise forms.ValidationError('Bag Number already Used')
        except Bags.DoesNotExist:
            return bag_number

    def save(self, emp, commit=False):
        cbag = super(ConsolidateBagForm, self).save(commit=commit)
        cbag.origin = emp.service_centre
        cbag.current_sc = emp.service_centre
        cbag.created_by = emp
        cbag.save()
        return cbag
