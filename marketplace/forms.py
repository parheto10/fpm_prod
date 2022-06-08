from django import forms
from .models import Souscripteur, Souscription

class SectionForm(forms.ModelForm):
    class Meta:
        model = Souscripteur
        widgets = {
            # "cooperative": CooperativeWidget,
            #"co_authors": CoAuthorsWidget,
        }
        fields = [
            'libelle',
            'responsable',
            'contacts',
        ]