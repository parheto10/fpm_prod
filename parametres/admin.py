from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Fournisseur,
    Intitule_Formation,
    Role,
    Sous_Prefecture,
    Origine,
    Prime,
    Projet,
    Activite,
    Region,
    Campagne,
    Espece,
    Cat_Plant,
    Projet_Cat,
    Cooperative,
    ObsMonitoring,
    Pepiniere,
    Semence_Pepiniere,
    Utilisateur,
    #MonitoringObserves,
)

class DetailsSemencePepiniereAdmin(admin.TabularInline):

   model = Semence_Pepiniere
   extra = 0

class CooperativeResource(resources.ModelResource):

    class Meta:
        model = Cooperative

class CooperativeAdmin(ImportExportModelAdmin):
    # list_display_links = ('contacts',)
    resource_class = CooperativeResource

class EspeceResource(resources.ModelResource):
    class Meta:
        model = Espece

class EspeceAdmin(ImportExportModelAdmin):
    resource_class = EspeceResource

class PepiniereAdmin(ImportExportModelAdmin):
   inlines = [DetailsSemencePepiniereAdmin]
   # inlines = [Details_RetraitAdmin]

class UtilisateurUserInlines(admin.StackedInline):
    model = Utilisateur

class UtilisateurUserAdmin(UserAdmin):
    inlines = (UtilisateurUserInlines, )

admin.site.register(Cooperative, CooperativeAdmin)
admin.site.unregister(User)
admin.site.register(User, UtilisateurUserAdmin)
admin.site.register(Activite)
admin.site.register(Campagne)
admin.site.register(Espece, EspeceAdmin)
admin.site.register(Prime)
admin.site.register(Origine)
admin.site.register(Projet)
admin.site.register(Region)
admin.site.register(Sous_Prefecture)
admin.site.register(Cat_Plant)
admin.site.register(Projet_Cat)
#admin.site.register(MonitoringObserves)
admin.site.register(Fournisseur)
admin.site.register(Role)
admin.site.register(ObsMonitoring)
admin.site.register(Pepiniere, PepiniereAdmin)
admin.site.register(Intitule_Formation)


# Register your models here.
