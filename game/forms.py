from django import forms
from .models import Postava

class PostavaForm(forms.ModelForm):
    class Meta:
        model = Postava
        # Tu povieme, ktoré polia chcemevo formulári vidieť
        fields = ['meno', 'hp', 'max_hp', 'sila']