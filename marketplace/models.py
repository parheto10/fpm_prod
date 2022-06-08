import os
import uuid
import time
import datetime
from django.contrib.auth.models import User
from django.db import models
#from django_countries.fields import CountryField

from parametres.models import Region, Projet


def upload_images(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "images/" + ".jpeg"


GENRE = (
        ('H', 'HOMMME'),
        ('F', 'FEMME'),
    )

class Formule(models.Model):
    titre = models.CharField(max_length=255)
    prix = models.PositiveIntegerField(default=2500)
    arbre = models.PositiveIntegerField(default=0)
    details = models.TextField()

    def __str__(self):
        return "%s - %s" % (self.titre, self.prix)

    def save(self, force_insert=False, force_update=False):
        self.titre = self.titre.upper()
        super(Formule, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "FORMULES"
        verbose_name = "formule"

class Souscripteur(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True,primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=15, verbose_name="MATRICULE", unique=True, blank=True, null=True)
    genre = models.CharField(max_length=10, verbose_name="GENRE", choices=GENRE, default="H", blank=True, null=True)
    #pays = CountryField(blank_label='(Préciser Votre Pays)')
    contact = models.CharField(max_length=50, verbose_name="TELEPHONE 1", help_text="Veuillez entrer un Numero Au format International Exple: +225 xx xx xx xx xx")
    adresse = models.CharField(max_length=255, verbose_name="ADRESSE", blank=True, null=True)
    image = models.ImageField(upload_to="upload_image", blank=True, null=True)
    add_le = models.DateTimeField(auto_now_add=True)
    update_le = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return ("%s - %s") %(self.user.username, self.matricule)

    def clean(self):
        # numerotation automatique
        if not self.id:
            tot = Souscripteur.objects.count()
            numero = tot
            madate = datetime.date.today()
            self.matricule = "%s-%s" % (numero, datetime.date.strftime(madate, '%d/%m/%Y'))

    class Meta:
        verbose_name_plural = "SOUSCRIPTEURS"
        verbose_name = "souscripteur"
        ordering = ["-add_le"]

class Souscription(models.Model):
    souscripteur = models.ForeignKey(Souscripteur, on_delete=models.CASCADE, related_name='abonnement')
    formule = models.ForeignKey(Formule, on_delete=models.CASCADE, related_name='formule_souscription')
    region= models.ForeignKey(Region, on_delete=models.CASCADE)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    prix = models.PositiveIntegerField(default=0, blank=True)
    arbre = models.PositiveIntegerField(default=0, blank=True)
    is_abonne = models.BooleanField(default=False)
    add_le = models.DateTimeField(auto_now_add=True)
    update_le = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return ('%s - %s') % (self.souscripteur.user.username, self.formule.prix)

    class Meta:
        verbose_name_plural = "SOUSCRIPTIONS"
        verbose_name = "souscription"
        # ordering = ["-add_le"]
