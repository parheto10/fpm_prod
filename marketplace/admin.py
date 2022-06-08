from django.contrib import admin
from .models import Souscripteur, Formule, Souscription

admin.site.register(Souscripteur)
admin.site.register(Formule)
admin.site.register(Souscription)

# Register your models here.
