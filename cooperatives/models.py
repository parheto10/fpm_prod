# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from email.policy import default
import os
from pickle import TRUE
import time
import uuid
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import datetime

from django.db.models import Sum, Count
from django.http import request
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from parametres.models import Campagne, Cooperative, Espece, Intitule_Formation, ObsMonitoring, Origine, Projet, Sous_Prefecture
# Create your models here.

ANNEES = []
for r in range(2010, (datetime.datetime.now().year+1)):
    ANNEES.append((r,r))

def producteurs_images(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "producteurs/images/" + self.code + ".jpeg"

def producteurs_documents(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "producteurs/documents/" + self.code

def upload_logo_site(self, filename):
    # verification de l'extension
    real_name, extension = os.path.splitext(filename)
    name = str(int(time.time())) + extension
    return "logos/" + self.code + ".jpeg"

TYPE_PRODUCTEUR = (
    ('MEMBRE', "MEMBRE"),
    ('USAGER', "USAGER"),
)

NATURE_DOC = (
    ('AUCUN', 'AUCUN'),
    ('ATTESTATION', 'ATTESTATION'),
    ('CNI', 'CNI'),
    ('PASSEPORT', 'PASSEPORT'),
    ('SEJOUR', 'CARTE DE SEJOUR'),
    ('CONSULAIRE', 'CARTE CONSULAIRE'),
)

CULTURE = (
    ('ANACARDE', 'ANACARDE'),
    ('CACAO', 'CACAO'),
    ('CAFE', 'CAFE'),
    ('COTON', 'COTON'),
    ('HEVEA', 'HEVEA'),
    ('PALMIER', 'PALMIER A HUILE'),
    ('SOJA', 'SOJA'),
    ('AUTRE', 'AUTRE'),
)

CERTIFICATION = (
    ('UTZ', 'UTZ'),
    ('RA', 'RA'),
    ('BIO', 'BIO'),
    ('PROJET', 'PROJET'),
    ('AUTRE', 'AUTRE'),
)

GENRE = (
    ('H', "HOMME"),
    ('F', "FEMME"),
)

SATISFACTION = (
    ('SATISFAIT','SATISFAIT'),
    ('COMPRIS','COMPRIS'),
    ('NOSATISFAIT','PAS SATISFAIT'),
    ('PASCOMPRIS','PAS COMPRIS')
)

ACQUISITION = (
    ('HERITAGE', 'HERITAGE'),
    ('ACHAT', 'ACHAT'),
    ('AUTRES', 'AUTRES'),
)

MODEL_AGRO = (
    ("AUTOUR", "AUTOUR"),
    ("CENTRE", "AUTOUR & CENTRE"),
)

CAMPAGNEPROD = (
    ('PETITE', 'PETITE CAMPAGNE'),
    ('GRANDE', 'GRANDE CAMPAGNE'),
)

TYPE_PARCELLE = (
    ("AGROFORESTERIE", "AGROFORESTERIE"),
    ("COMMUNAUTAIRE", "COMMUNAUTAIRE"),
    ("FORET_CLASSEE", "FORET CLASSEE"),
    ("INDIVIDUELLE", "INDIVIDUELLE"),
    ("JACHERE", "JACHERE"),
    ("PRIVEE", "PRIVEE"),
)


class Section(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="sections")
    libelle = models.CharField(max_length=250)
    responsable = models.CharField(max_length=250, blank=True, null=True)
    contacts = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return '%s' %(self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        if self.responsable:
            self.responsable = self.responsable.upper()
        super(Section, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "SECTIONS"
        verbose_name = "section"
        ordering = ["libelle"]


class Sous_Section(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=250)
    responsable = models.CharField(max_length=250, blank=True, null=True)
    contacts = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return '%s' %(self.libelle)

    def save(self, force_insert=False, force_update=False):
        self.libelle = self.libelle.upper()
        if self.responsable:
            self.responsable = self.responsable.upper()
        super(Sous_Section, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "SOUS SECTIONS"
        verbose_name = "sous section"
        ordering = ["libelle"]

class Producteur(models.Model): 
    code = models.CharField(max_length=150,  verbose_name='CODE PRODUCTEUR',unique=True,primary_key=True,null=False,editable=True)
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name='producteurs')
    origine = models.ForeignKey(Origine, on_delete=models.CASCADE, related_name='producteurs', default=1)
    sous_prefecture = models.ForeignKey(Sous_Prefecture, on_delete=models.SET_NULL, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='producteurs')
    sous_section = models.ForeignKey(Sous_Section, related_name="sous_section", on_delete=models.CASCADE, blank=True,null=True)
    type_producteur = models.CharField(max_length=50, verbose_name="TYPE PRODUCTEUR", choices=TYPE_PRODUCTEUR,default="MEMBRE")
    genre = models.CharField(max_length=2, choices=GENRE, default="H")
    nom = models.CharField(max_length=250,  verbose_name="Nom et prénoms")
    dob = models.DateField(blank=True, null=True, verbose_name="Date/Année de Naissance")
    contacts = models.CharField(max_length=50, blank=True, null=True)
    localite = models.CharField(max_length=100, blank=True, null=True)
    nb_enfant = models.PositiveIntegerField(default=0, null=True, blank=True)
    nb_epouse = models.PositiveIntegerField(default=0, null=True, blank=True)
    enfant_scolarise = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="Enfant Scolarise")
    nb_personne = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="Personne à Charge")
    nb_parcelle = models.PositiveIntegerField(default=0)
    image = models.ImageField(verbose_name="Logo", upload_to=producteurs_images, blank=True)
    type_document = models.CharField(max_length=50, verbose_name="TYPE DOCUMENT", choices=NATURE_DOC, default="AUCUN")
    num_document = models.CharField(max_length=150, verbose_name="N° PIECE", null=True, blank=True)
    document = models.FileField(verbose_name="Documents", upload_to=producteurs_documents, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    objects = models.Manager()


    def __str__(self):
        return '%s' %(self.nom)

    def Producteur(self):
        return '%s - %s' % ( self.code, self.nom)

    def save(self, force_insert=False, force_update=False,using=None):
        self.code = self.code.upper()
        super(Producteur, self).save(force_insert, force_update,using)

    def clean(self):
        if self.document != "" and self.type_document == "":
            raise ValidationError('Veuillez Charger le Document Approprié SVP')
        else:
            pass
        

    def Photo(self):
        if self.image:
            photoLink = "/media/%s" % self.image
            thumb = mark_safe('<img src="%s" style="width: 45px; height:45px;" />' % self.image.url)
            return "<img src='%s' />" % thumb.url
        elif self.genre == "H":
            thumb = mark_safe('<img src="127.0.0.1:8000/static/img/logo_homme.jpeg" style="width: 45px; height:45px;" />')
            # thumb = get_thumbnail('127.0.0.1:8000/static/img/logo_home.jpeg', "60x60", crop='center', quality=99)
            return "<img src='%s' />" % thumb
            # return ""
        else:
            thumb = mark_safe('<img src="127.0.0.1:8000/static/img/logo_femme.jpeg" style="width: 45px; height:45px;" />')
            return "<img src='%s' />" % thumb
            # return "127.0.0.1:8000/img/avatar3.png"
            # return "Aucun logo"

    Photo.short_description = "Logo"
    Photo.allow_tags = True

    class Meta:
        verbose_name_plural = "PRODUCTEURS"
        verbose_name = "producteur"
        ordering = ["-created_at"]


class Parcelle(models.Model):
    code = models.CharField(max_length=150,unique=True,primary_key=True,verbose_name='CODE PARCELLE', help_text="LE CODE PARCELLE EST GENERE AUTOMATIQUEMENT")
    code_certificat = models.CharField(max_length=150, blank=True, null=True, verbose_name='CODE certification')
    type_parcelle = models.CharField(max_length=50, choices=TYPE_PARCELLE, default="AGROFORESTERIE")
    annee_certificat = models.IntegerField(verbose_name='Année certification', choices=ANNEES,blank=True, null=True)
    annee_acquis = models.IntegerField(verbose_name='Année acquisition', choices=ANNEES,blank=True, null=True)
    producteur = models.ForeignKey(Producteur, related_name='parcelles', on_delete=models.CASCADE)
    acquisition = models.CharField(max_length=50, verbose_name="MODE ACQUISITION", choices=ACQUISITION, default="heritage")
    latitude = models.CharField(max_length=12, null=True, blank=True)
    longitude = models.CharField(max_length=12, null=True, blank=True)
    superficie = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    culture = models.CharField(max_length=50, verbose_name="CULTURE", choices=CULTURE, default="cacao")
    certification = models.CharField(max_length=50, verbose_name="CERTIFICATION", choices=CERTIFICATION, default="utz")
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, default=1)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    objects = models.Manager()

    def __str__(self):
        if self.code:
            return "%s - %s" % (self.code, self.producteur)
        else:
            return "%s - %s" % (self.producteur.code, self.producteur)

    def coordonnees(self):
        return str(self.longitude) + ', ' + str(self.latitude)

    class Meta:
        verbose_name_plural = "PARCELLES"
        verbose_name = "parcelle"
        ordering = ["-created_at"]


class Planting(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE PLANTING')
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name="plantings")
    nb_plant_exitant = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS EXISTANTS")
    plant_recus = models.PositiveIntegerField(default=0, verbose_name="NOMBRE DE PLANTS RECUS")
    plant_total = models.PositiveIntegerField(default=0, verbose_name="NOMBRE TOTAL DE PLANTS")
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, related_name="plantings")
    date = models.DateField()
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    #def get_absolute_url(self):
    #    return reverse('cooperatives:suivi_planting', kwargs={'pk': self.pk})

    def __str__(self):
        return '%s - (%s) plants reçus' % (self.parcelle.producteur, self.parcelle)

    def save(self, force_insert=False, force_update=False,using=None):
        self.plant_total = (self.nb_plant_exitant) + (self.plant_recus)
        super(Planting, self).save(force_insert, force_update,using)

    class Meta:
        verbose_name_plural = "PLANTINGS"
        verbose_name = "planting"
        ordering = ["-date"]
        get_latest_by = ['date']
        

class DetailPlanting(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
    planting = models.ForeignKey(Planting, on_delete=models.CASCADE)
    espece = models.ForeignKey(Espece, on_delete=models.CASCADE, default=1)
    nb_plante = models.PositiveIntegerField(default=0, verbose_name="QTE recu")
    etat = models.IntegerField(null= True, blank = True, default = 0)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('cooperatives:suivi_planting',args=[self.planting.code])


    class Meta:
        verbose_name_plural = "DETAILS PLANTINGS"
        verbose_name = "details planting"


class Monitoring(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
    planting = models.ForeignKey(Planting, on_delete=models.CASCADE)
    mort_global = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS MORTS",blank=True,null=True)
    mature_global = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS VIVANTS",blank=True,null=True)
    observation = models.ManyToManyField(ObsMonitoring,related_name="cooperatives_monitoring_observation",blank=True)
    date = models.DateField()
    taux_vitalite = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    taux_mortalite = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = "MONITORINGS PLANTINGS"
        verbose_name = "monitoring planting"
    
    def save(self, force_insert=False, force_update=False,using=None):
        if self.mature_global:
            self.taux_vitalite = ((self.mature_global*100)/(self.planting.plant_recus))
            self.taux_mortalite = 100 - self.taux_vitalite       
        super(Monitoring, self).save(force_insert, force_update,using)

    def get_observation(self):
        ret = ''
        for obs in self.observation.all():
            ret = ret + obs.libelle + ' , '
        return ret[:-1]

class RemplacementMonitoring(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
    date = models.DateField()
    espece = models.ManyToManyField(Espece,through="MonitoringEspeceremplacement")
    monitoring = models.ForeignKey(Monitoring,on_delete=models.CASCADE)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)


class DetailPlantingRemplacement(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
    planting = models.ForeignKey(Planting, on_delete=models.CASCADE)
    espece = models.ForeignKey(Espece, on_delete=models.CASCADE)
    nb_plante = models.PositiveIntegerField(default=0, verbose_name="QTE recu")
    remplacer = models.ForeignKey(RemplacementMonitoring, on_delete=models.SET_NULL,null=True)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    objects = models.Manager()

    class Meta:
        verbose_name_plural = "DETAILS PLANTINGS APRES REMPLACEMENT"
        verbose_name = "details planting remplacement"


class DetailMonitoring(models.Model):
   code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
   monitoring = models.ForeignKey(Monitoring, on_delete=models.CASCADE)
   espece = models.ManyToManyField(Espece,through='MonitoringEspece')
   created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
   user_id = models.IntegerField(null=True,blank=True)
   synchro = models.CharField(max_length=10, default='OUI')
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
        verbose_name_plural = "DETAILS MONITORINGS "
        verbose_name = "details monitoring"


class MonitoringEspece(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
    detailmonitoring = models.ForeignKey(DetailMonitoring, on_delete=models.CASCADE)
    espece = models.ForeignKey(Espece, on_delete=models.CASCADE)
    detailplanting = models.ForeignKey(DetailPlanting, on_delete=models.SET_NULL,null=True)
    mort = models.PositiveIntegerField(default=0, verbose_name="NBRE PLANTS MORTS")
    detailplantingremplacement = models.ForeignKey(DetailPlantingRemplacement, on_delete=models.SET_NULL,null=True)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    taux_mortalite = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False,using=None):

        if self.detailplantingremplacement  :
            if self.mort or self.mort > 0:
                self.taux_mortalite = ((self.mort*100)/(self.detailplantingremplacement.nb_plante))
            elif self.mort == 0:
                self.taux_mortalite = 0
        else:
            if self.mort or self.mort > 0:
                self.taux_mortalite = ((self.mort*100)/(self.detailplanting.nb_plante))
            elif self.mort == 0:
                self.taux_mortalite = 0
                #self.taux_mortalite = 100 - self.taux_vitalite        
        super(MonitoringEspece, self).save(force_insert, force_update,using)
    

class Participantcoop(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255,unique=TRUE)
    contact  = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' %(self.nom)

    def save(self, force_insert=False, force_update=False):
        self.nom = self.nom.upper()
        super(Participantcoop, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "PARTICIPANTS DE LA COOPERATIVE"
        verbose_name = "participant de la cooperative"
       # ordering = ["nom"]


class Formation(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE)
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE)
    formateur = models.CharField(max_length=255, verbose_name="FORMATEUR")
    structureformateur = models.CharField(max_length=100,verbose_name="STRUCTURE FORMATEUR",blank=True,null=True)
    niveauformateur = models.CharField(max_length=100,verbose_name="NIVEAU ETUDE FORMATEUR",blank=True,null=True)
    intitule  = models.ForeignKey(Intitule_Formation,on_delete=models.CASCADE)
    note_formateur = models.TextField(blank=True,null=True)
    participant = models.ManyToManyField(Participantcoop,through="Participantformation")
    critere = models.CharField(max_length=50,choices=SATISFACTION,blank=True,null=True,default="")
    debut = models.DateField(verbose_name="DATE DEBUT")
    fin = models.DateField(verbose_name="DATE FIN")
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return "%s" %(self.formateur)

    def Duree(self):
        delta = (self.fin - self.debut).days
        return delta - (delta // 7) * 2 #calcul nombrede jours travailler(sans week-end)


class Participantformation(models.Model):
    formation = models.ForeignKey(Formation,on_delete=models.CASCADE)
    participant = models.ForeignKey(Participantcoop, on_delete=models.SET_NULL,null=True)
    nom = models.CharField(max_length=255)
    #localite = models.CharField(max_length=255)
    contact  = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s - %s - %s"  %(self.nom,self.formation,self.participant)

    def save(self, force_insert=False, force_update=False):
        self.nom = self.nom.upper()
        super(Participantformation, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural = "PARTICIPANTS DE LA FORMATION"
        verbose_name = "participant de la formation"
        ordering = ["nom"]#ui


class Detail_Formation(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    participant = models.ManyToManyField(Producteur)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def Participants(self):
        nb_participants = self.participant.all().count()
        return nb_participants

    def __str__(self):
        return "%s" % (self.formation)

    class Meta:
        verbose_name_plural = "DETAILS FORMATIONS"
        verbose_name = "details formation"
        ordering = ["formation"]


class MonitoringEspeceremplacement(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
    remplacement = models.ForeignKey(RemplacementMonitoring,on_delete=models.CASCADE)
    espece = models.ForeignKey(Espece,on_delete=models.CASCADE)
    recu = models.PositiveIntegerField(default=0,verbose_name="NOMBRE PLANTS RECU",blank=True,null=True)
    remplacer = models.PositiveBigIntegerField(default=0,verbose_name="NOMBRE PLANTS REMPLACER",blank=True,null=True)
    mort = models.PositiveBigIntegerField(default=0,verbose_name="NOMBRE PLANTS MORT",blank=True,null=True)
    futur = models.PositiveBigIntegerField(default=0,verbose_name="NOMBRE PLANTS PROCHAIN REMPLACEMENT",blank=True,null=True)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)




 
class Production(models.Model):
    code = models.CharField(max_length=150, blank=True,unique=True,primary_key=True,null=False,editable=True,verbose_name='CODE ')
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    # campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE)
    campagne = models.CharField(max_length=150, choices=CAMPAGNEPROD, default='PETITE')
    qteProduct = models.IntegerField(default=0)
    created_at = models.CharField(max_length=150,default=datetime.datetime.now().year)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s(%s) - %s' %(self.parcelle,self.qteProduct, self.campagne)

    class Meta:
        verbose_name_plural = "PRODUCTIONS/PARCELLES"
        verbose_name = "production/parcelle"
        
        

##########28/06/2022#############MPI###########HISTORIQUE##########

class SyncHistorique(models.Model):
    date = models.DateField()
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(null=True,blank=True,default=0)
    indice = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class MonitoringObsMobile(models.Model):
    monitoring = models.ForeignKey(Monitoring, on_delete= models.CASCADE)
    observation = models.ForeignKey(ObsMonitoring, on_delete=models.CASCADE)
    user_id = models.IntegerField(null=True,blank=True)
    synchro = models.CharField(max_length=10, default='OUI')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


class ImportProdFileModel(models.Model):
    code = models.CharField(max_length=150,  verbose_name='CODE PRODUCTEUR',unique=True,primary_key=True,null=False,editable=True)
    nom = models.CharField(max_length=250,  verbose_name="Nom et prénoms")
    localite = models.CharField(max_length=100, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL,null=True)
    nb_parcelle = models.PositiveIntegerField(default=0)
    genre = models.CharField(max_length=2, choices=GENRE, default="H",blank=True, null=True)
    dob = models.DateField(blank=True, null=True, verbose_name="Date/Année de Naissance")
    contacts = models.CharField(max_length=50, blank=True, null=True)
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE)
    user_id = models.IntegerField(null=True,blank=True)
    nom_prime = models.CharField(max_length=250,  verbose_name="Nom et prénoms",null=True,blank=True)
    localite_prime = models.CharField(max_length=100, blank=True, null=True)
    section_prime = models.IntegerField(null=True,blank=True)
    nb_parcelle_prime = models.PositiveIntegerField(null=True,blank=True)
    genre_prime = models.CharField(max_length=2,null=True,blank=True)
    dob_prime = models.DateField(blank=True, null=True, verbose_name="Date/Année de Naissance")
    contacts_prime = models.CharField(max_length=50, blank=True, null=True)
    cooperative_prime = models.IntegerField(null=True,blank=True)
    user_id_prime = models.IntegerField(null=True,blank=True)
    etatValidate = models.CharField(max_length=50,default="EN ATTENTE", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    