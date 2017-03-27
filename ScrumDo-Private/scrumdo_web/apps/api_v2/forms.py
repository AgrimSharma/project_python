from django import forms
from piston.models import Consumer

class ConsumerForm(forms.ModelForm):    
    
    class Meta:
        model = Consumer
        fields = ('name', 'description')
