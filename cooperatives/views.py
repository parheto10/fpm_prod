import datetime

import datetime
import os
import re
import sys
import uuid
import pandas as pd
#from numpy import iterable
#from pandas import notnull

import requests
from django.conf import settings
from django.contrib.staticfiles import finders
from rest_framework.response import Response
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
# from django.contrib.gis.serializers import geojson
from django.core.serializers import serialize
from django.core import serializers
from django.http import HttpResponse, QueryDict
from django.db.models import Sum, Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
#import folium
#from django_pandas.io import read_frame
#from folium import raster_layers, plugins, Popup
import json
from django.template.loader import get_template, render_to_string
from django.views.generic import TemplateView
#from folium.plugins import MarkerCluster
from rest_framework.decorators import api_view
#from xhtml2pdf import pisa
from django.views import View
from xhtml2pdf import pisa
from xlrd.formatting import Format
from django.core.files.storage import FileSystemStorage

# Import django Serializer Features #
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from parametres.forms import UserForm
from parametres.models import Intitule_Formation, Projet, Espece, Campagne, Role, Utilisateur
from parametres.serializers import DetailMonitoringSerializer, DetailsPlantingSerializer, MonitoringEspeceSerializer, MonitoringSerializer, ParcelleSerializer, PlantingSerializer, ProducteurDataTableSerializer, ProducteurSerializer
from .forms import CoopForm, EditProductionForm, MonitoringEspeceForm, ParticipantcoopForm, ProdForm, EditProdForm, ParcelleForm, RemplacementMonitoringForm, SectionForm, Sous_SectionForm, \
     FormationForm, DetailFormation, EditFormationForm, EditParcelleForm, Edit_Sous_SectionForm, MonitoringForm, \
    PlantingForm, DetailPlantingForm, ProductionForm
from .models import Cooperative, DetailMonitoring, DetailPlantingRemplacement, ImportProdFileModel, MonitoringEspece, \
    MonitoringEspeceremplacement,MonitoringObsMobile, Participantcoop, Participantformation, RemplacementMonitoring, Section, Sous_Section, \
    Producteur, Parcelle, Planting, Formation, Detail_Formation, \
    DetailPlanting, Monitoring, Production, SyncHistorique
from .serializers import CooperativeSerliazer, ParcelleSerliazer
from django.db.models import Q


def is_cooperative(user):
    return user.groups.filter(name='COOPERATIVES').exists()

#@login_required(login_url='connexion')
#@user_passes_test(is_cooperative)
# def cooperative(request, id=None):
#     coop = get_object_or_404(Cooperative, pk=id)
#     producteurs = Producteur.objects.all().filter(section__cooperative_id= coop)
#     nb_producteurs = Producteur.objects.all().filter(section__cooperative_id= coop).count()
#     parcelles = Parcelle.objects.all().filter(propietaire__section__cooperative_id=coop)
#     nb_parcelles = Parcelle.objects.all().filter(propietaire__section__cooperative_id=coop).count()
#     context = {
#         "coop": coop,
#         'cooperative': cooperative,
#         'producteurs': producteurs,
#         'nb_producteurs': nb_producteurs,
#         'parcelles': parcelles,
#         'nb_parcelles': nb_parcelles,
#     }
#     return render(request, "cooperatives/dashboard.html", context)

@login_required(login_url='connexion')
def coop_dashboard(request):
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    producteurs = Producteur.objects.filter(cooperative_id=cooperative)
    nb_producteurs = Producteur.objects.filter(cooperative_id=cooperative).count()
    nb_formations = Formation.objects.all().filter(cooperative_id=cooperative).count()
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    nb_parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).count()
    Superficie = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    Plants = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('plant_total'))['total']
    section = Section.objects.all().filter(cooperative_id=cooperative)
    section_prod = Section.objects.annotate(nb_producteur=Count('producteurs'))
    section_parcelles = Parcelle.objects.filter(producteur__section_id__in=section).count()
    section_superf = Parcelle.objects.filter(producteur__section_id__in=section).aggregate(total=Sum('superficie'))['total']
    section_planting = DetailPlanting.objects.filter(planting__parcelle__producteur__section_id__in=section).aggregate(total=Sum('nb_plante'))['total']
    # detail_planting = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative)#.annotate(nb_plante=Sum('nb_plante'))
    espece_planting = Espece.objects.all()
    plantings = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plante'))['total']
    coop_plants = DetailPlanting.objects.filter(espece_id__in=espece_planting).aggregate(total=Sum('nb_plante'))['total']
    #production = (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total']) / 1000
    production = 0
    if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total']) != None:
        production = (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total'])  / 1000
    else :
        production = (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total'])

    petite_production = 0
    if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total']) != None :
        petite_production = (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total']) / 1000

    grande_production = 0
    if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total']) != None :
        grande_production = (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total']) / 1000

    #petite_production = (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total']) / 1000
    #grande_production = (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total']) / 1000
    #production_section = Production.objects.filter(parcelle__producteur__section_id=section)
    # plantings = DetailPlanting.objects.values("espece__libelle").filter(planting__parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('nb_plante'))['total']
    # print(plantings)
    # espece_planting = DetailPlanting.objects.filter(espece__libelle__in=details_planting).aggregate(total=Sum('nb_plante'))['total']
    # espece_planting = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).annotate(nb_plante=Sum('nb_plante'))
    # print(section_prod)
    # nb_producteurs = sections.producteur.set_all()
    # querysets = Detail_Retrait_plant.objects.values("espece__libelle").filter(retait__pepiniere__cooperative_id=cooperative).annotate(plant_retire=Sum('plant_retire'))
    # semences = Semence_Pepiniere.objects.values("espece_recu__libelle").filter(pepiniere__cooperative_id=cooperative).annotate(qte_recu=Sum('qte_recu'))
    activate = "cooperative"
    context={
    'cooperative':cooperative,
    'producteurs': producteurs,
    'nb_producteurs': nb_producteurs,
    'nb_formations': nb_formations,
    'section_prod': section_prod,
    'section_parcelles': section_parcelles,
    'section_superf': section_superf,
    'parcelles': parcelles,
    'nb_parcelles': nb_parcelles,
    'Superficie' : Superficie,
    'Plants': Plants,
    'section': section,
    'section_planting': section_planting,
    'espece_planting': espece_planting,
    'plantings': plantings,
    'coop_plants': coop_plants,
    'production': production,
    'petite_production': petite_production,
    'grande_production': grande_production,
    'activate':activate,
    'role':role
    # 'labels': labels,
    # 'data': data,
    # 'mylabels': mylabels,
    # 'mydata': mydata,
    }
    return render(request,'cooperatives/dashboard.html',context=context)

def coopdetailPlantings(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    querysets = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data= {
        'labels':labels,
        'data':data,
    })

# def prod_section(request):
#     cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
#     semences = Semence_Pepiniere.objects.values("espece_recu__libelle").filter(pepiniere__cooperative_id=cooperative).annotate(qte_recu=Sum('qte_recu'))
#     labels = []
#     data = []
#     for stat in semences:
#         labels.append(stat['espece_recu__libelle'])
#         data.append(stat['qte_recu'])
#
#     return JsonResponse(data= {
#         'labels':labels,
#         'data':data,
#     })

@login_required(login_url='connexion')
def add_section(request):
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    sections = Section.objects.all().filter(cooperative_id=cooperative)
    form = SectionForm()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.cooperative_id = cooperative.id
            section = section.save()
            # print()
        messages.success(request, "Section Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:section'))
    context = {
        "cooperative": cooperative,
        "sections": sections,
        'form': form,
        'role':role
    }
    return render(request, "cooperatives/sections.html", context)



def delete_section(request, id=None):
    item = get_object_or_404(Section, id=id)
    if request.method == "POST":
        item.delete()
        messages.error(request, "Section Supprimée Avec Succès")
        return redirect('cooperatives:section')
    context = {
        # 'pepiniere': pepiniere,
        'item': item,
    }
    return render(request, 'cooperatives/section_delete.html', context)
    # item.delete()
    # messages.success(request, "Section Supprimer avec Succès")
    # return HttpResponseRedirect(reverse('cooperatives:section'))

@login_required(login_url='connexion')
def add_sous_section(request):
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    sections = Section.objects.all().filter(cooperative_id=cooperative)
    sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    form = Sous_SectionForm()
    if request.method == 'POST':
        form = Sous_SectionForm(request.POST)
        if form.is_valid():
            sous_section = form.save(commit=False)
            sous_section = sous_section.save()
        messages.success(request, "Sous Section Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:sous_sections'))
    context = {
        "cooperative": cooperative,
        "sous_sections": sous_sections,
        "sections": sections,
        'form': form,
        'role':role
    }
    return render(request, "cooperatives/sous_sections.html", context)





def my_section(request):
    cooperative = request.GET.get("user_id")
    coop_sections = Section.objects.filter(cooperative_id=cooperative)
    context = {'coop_sections': coop_sections}
    return render(request, 'cooperatives/section.html', context)


@login_required(login_url='connexion')
def producteurs(request):
    activate = "producteurs"
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    # producteurs = Producteur.objects.filter(cooperative_id=cooperative)#.order_by("-add_le")
    sections = Section.objects.filter(id= 44) | Section.objects.filter(cooperative_id = cooperative)
    sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)

    prodForm = ProdForm()
    context = {
        "cooperative":cooperative,
        # "producteurs": producteurs,
        'prodForm': prodForm,
        'sections':sections,
        'sous_sections':sous_sections,
        'activate':activate,
        'role':role

    }
    return render(request, "cooperatives/producteurs.html", context)


def prod_delete(request, code=None):
    item = get_object_or_404(Producteur, code=code)
    item.delete()
    try :
        importProd = get_object_or_404(ImportProdFileModel, code = code)
        importProd.delete()
    except ImportProdFileModel.DoesNotExist :
        pass
    


@login_required(login_url='connexion')
def parcelles(request):
    activate = "parcelles"
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    prods = Producteur.objects.filter(cooperative_id=cooperative)
    s_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    # parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    parcelleForm = ParcelleForm(request.POST or None)

    context = {
        "cooperative":cooperative,
        # "parcelles": parcelles,
        'parcelleForm': parcelleForm,
        'producteurs': prods,
        's_sections': s_sections,
        'activate': activate,
        'role':role
    }
    return render(request, "cooperatives/parcelles.html", context)



def parcelle_delete(request, code=None):
    parcelle = get_object_or_404(Parcelle, code=code)
    parcelle.delete()


def detail_parcelles(request, code=None):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    plantings = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative)
    instance = get_object_or_404(Planting, code=code)
    # details = Details_planting.objects.all().filter(planting_id=instance)

    context = {

    }

    return render(request, 'cooperatives/detail_parcelle', context)


# def planting(request):
#     cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
#     # producteurs = Producteur.objects.all().filter(cooperative=cooperative)
#     parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
#     plantings = Planting.objects.all().filter(parcelle__producteur__cooperative_id=cooperative)
#     plantingForm = PlantingForm()
#     if request.method == 'POST':
#         plantingForm = PlantingForm(request.POST, request.FILES)
#         if plantingForm.is_valid():
#             planting = plantingForm.save(commit=False)
#             for parcelle in parcelles.iterator():
#                 planting.parcelle_id = parcelle.id
#             planting = planting.save()
#             print(planting)
#             # print(planting.parcelle.producteur)
#         messages.success(request, "Parcelle Ajoutés avec succès")
#         return HttpResponseRedirect(reverse('cooperatives:planting'))
#     context = {
#         "cooperative":cooperative,
#         "parcelles": parcelles,
#         "plantings": plantings,
#         'plantingForm': plantingForm,
#     }
#     return render(request, "cooperatives/plantings.html", context)

# def suivi_planting(request, id=None):
#     instance = get_object_or_404(Planting, id=id)
#     # details = Details_planting.objects.all().filter(planting_id=instance)
#
#     # suiviForm = SuiviPlantingForm()
#     # if request.method == 'POST':
#     #     suiviForm = SuiviPlantingForm(request.POST, request.FILES)
#     #     if suiviForm.is_valid():
#     #         suivi = suiviForm.save(commit=False)
#     #         suivi.planting_id = instance.id
#     #         suivi = suivi.save()
#     #         print(suivi)
#     #     messages.success(request, "Planting Ajouté avec succès")
#     #     return HttpResponseRedirect(reverse('cooperatives:planting'))
#     # context = {
#     #     'instance':instance,
#     #     'details':details,
#     #     'suiviForm':suiviForm,
#     # }
#     # return render(request, 'cooperatives/suivi_planting.html', context)

# def planting_update(request, id=None):
# 	instance = get_object_or_404(Planting, id=id)
# 	# form = PlantingForm(request.POST or None, request.FILES or None, instance=instance)
# 	if form.is_valid():
# 		instance = form.save(commit=False)
# 		instance.save()
# 		messages.success(request, "Modification effectuée avec succès")
# 		return HttpResponseRedirect(reverse('cooperatives:planting'))
#
# 	context = {
# 		"instance": instance,
# 		"form":form,
# 	}
# 	return render(request, "cooperatives/planting_edit.html", context)

#-------------------------------------------------------------------------
## Export to Excel
#-------------------------------------------------------------------------

import csv

from django.http import HttpResponse
from django.contrib.auth.models import User

def export_producteur_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="producteurs.csv"'

    writer = csv.writer(response)
    writer.writerow(['CODE', 'TYPE', 'SECTION', 'GENRE', 'NOM', 'PRENOMS', 'CONTACTS'])
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    # producteurs = Producteur.objects.all().filter(cooperative=cooperative)

    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'code',
        'type_producteur',
        'section__libelle',
        'genre',
        'nom',
        'prenoms',
        'contacts',
    )
    for p in producteurs:
        writer.writerow(p)

    return response

import xlwt

from django.http import HttpResponse
from django.contrib.auth.models import User

def export_prod_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'NOM ET PRENOMS', 'SECTION', 'LOCALITE', 'TYPE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    rows = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'code',
        'nom',
        'section__libelle',
        'localite',
        'type_producteur',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def export_planting_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'PRODUCTEUR', 'SECTION', 'ESPECE', 'QTE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    rows = DetailPlanting.objects.all().filter(planting__parcelle__producteur__cooperative_id=cooperative.id).values_list(
        'planting__parcelle__code',
        'planting__parcelle__producteur__nom',
        'planting__parcelle__producteur__section__libelle',
        'espece__libelle',
        'nb_plante',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_section_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Sections.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sections')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID','LIBELLE', 'RESPONSABLE', 'CONTACTS']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    rows = Section.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'id',
        'libelle',
        'responsable',
        'contacts',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_sous_section_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Sous Sections.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sous Sections')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['SECTION', 'LIBELLE', 'RESPONSABLE', 'CONTACTS']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    rows = Sous_Section.objects.all().filter(section__cooperative_id=cooperative.id).values_list(
        'section__libelle',
        'libelle',
        'responsable',
        'contacts',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_parcelle_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Parcelles.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Parcelles')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'PROPRIETAIRE', 'SECTION', 'LOCALITE', 'SUPERFICIE(Ha)', 'LATITUDE', 'LONGITUDE', 'CULTURE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    rows = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative.id).values_list(
        'code',
        'producteur__nom',
        'producteur__section__libelle',
        'producteur__localite',
        'superficie',
        'latitude',
        'longitude',
        'culture',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_formation_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Formations.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Formations')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['PROJET', 'FORMATEUR', 'INTITULE', 'DEBUT', 'FIN']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    # format2 = xlwt.Workbook({'num_format': 'dd/mm/yy'})
    rows = Formation.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'projet__titre',
        'formateur',
        'libelle',
        'debut',
        'fin',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if isinstance(row[col_num], datetime.datetime):
                DEBUT = row[col_num].strftime('%d/%m/%Y')
                FIN = row[col_num].strftime('%d/%m/%Y')
                ws.write(row_num, col_num, DEBUT, FIN, font_style)
            else:
                ws.write(row_num, col_num, row[col_num], font_style)
            # ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_plant_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Planting.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Plants')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['P.CODE', 'P.NOM', 'P.PRENOMS', 'PARCELLE', 'ESPECE', 'NOMBRE', 'DATE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    rows = Planting.objects.all().filter(parcelle__propietaire__cooperative_id=cooperative.id).values_list(
        'parcelle__propietaire__code',
        'parcelle__propietaire__nom',
        'parcelle__propietaire__prenoms',
        'parcelle__code',
        'espece',
        'nb_plant',
        'date',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

from io import BytesIO
#from reportlab.pdfgen import canvas
from django.http import HttpResponse

def export_prod_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Producteurs.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Start writing the PDF here
    p.drawString(100, 100, 'Hello world.')
    # End writing

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse

def localisation(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    # section = Section.objects.all().filter(cooperative_id=cooperative)
    sections = Section.objects.all().filter(cooperative_id=cooperative) #Parcelle.objects.filter(producteur__section_id__in=section)
    context = {
        'cooperative': cooperative,
        'parcelles' : parcelles,
        'sections' : sections
    }
    return render(request, 'cooperatives/carte_update.html', context)


@login_required(login_url='connexion')
def formation(request):
    activate = "formations"
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    themes = Intitule_Formation.objects.all()

    context = {
        'cooperative': cooperative,
        'themes': themes,
        'activate': activate,
        'role':role
    }
    return render(request, 'cooperatives/formations.html', context)

def Editformation(request, id=None):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    instance = get_object_or_404(Formation, id=id)
    form = EditFormationForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.cooperative_id = cooperative.id
        instance.save()
        instance.save()
        messages.success(request, "Modification Effectuée Avec Succès", extra_tags='html_safe')
        return HttpResponseRedirect(reverse('cooperatives:formations'))

    context = {
        "cooperative":cooperative,
        "instance": instance,
        "form": form,
    }
    return render(request, "cooperatives/edit_formation.html", context)

# def detail_formation(request, id=None):
#     cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
#     # instance = Detail_Formation.objects.get(formation_id=id)
#     instance = get_object_or_404(Formation, id=id)
#     details = Detail_Formation.objects.all().filter(formation_id=instance)
#     participants = Producteur.objects.all().filter(cooperative_id=cooperative)
#     form = DetailFormation()
#     if request.method == 'POST':
#         form = DetailFormation(request.POST, request.FILES)
#         if form.is_valid():
#             detail = form.save(commit=False)
#             detail.formation_id = instance.id
#             # for p in participants:
#                 # detail.
#             detail = detail.save()
#             # print(detail)
#             # print(planting.parcelle.producteur)
#         messages.success(request, "Formation Ajoutée avec succès")
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#         # return HttpResponseRedirect(reverse('cooperatives:formations'))
#     # participants = Producteur.objects.all().filter(formation_id=formation)
#     context = {
#         'instance': instance,
#         'details': details,
#         'form': form,
#         'participants': participants,
#     }
#     return render(request, 'cooperatives/detail_formation.html', context)

@login_required(login_url='connexion')
def detail_formation(request, id=None):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    theme = get_object_or_404(Intitule_Formation, id=id)
    formations = Formation.objects.filter(intitule_id = theme.id,cooperative_id=cooperative.id)



    for formation in formations :
        formation.nb_participant = Participantformation.objects.filter(formation_id = formation.id).count()



    context = {
        'theme': theme,
        'formations':formations,
        'cooperative':cooperative
    }


    return render(request, 'cooperatives/detail_formation.html', context)

#Parcelle Json
# def my_parcelles(request):
#     parcelles = Parcelle.objects.all()
#     parcelles_list = serializers.serialize('json', parcelles)
#     return HttpResponse(parcelles_list, content_type="text/json-comment-filtered")

# class ParcellesView(View):
#     def get(self, request, *args, **kwargs):
#         if request.is_ajax():
#             parcelles = Producteur.objects.all()
#             parcelles_serializers = serializers.serialize('json', parcelles)
#             return JsonResponse(parcelles_serializers, safe=False)
#         return JsonResponse({'message': 'Erreure Lors du Chargement.....'})
    # parcelles = Parcelle.objects.all()
    # parcelles_list = serializers.serialize('json', parcelles)
    # return HttpResponse(parcelles_list, content_type="text/json-comment-filtered")

# DJango Serializer Views#

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path
#Export PARCELLES to PDF
@login_required(login_url='connexion')
def export_prods_to_pdf(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    template_path = 'cooperatives/producteurs_pdf.html'
    context = {
        'cooperative':cooperative,
        'producteurs':producteurs,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Liste Producteur.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('Une Erreure est Survenue, Réessayer SVP...' + html + '</pre>')
    return response


def export_parcelles_to_pdf(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    template_path = 'cooperatives/new_parcelles_pdf.html'
    context = {
        'cooperative': cooperative,
        'parcelles': parcelles,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Liste Parcelles.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('Une Erreure est Survenue, Réessayer SVP...' + html + '</pre>')
    return response

@csrf_exempt
def parcelle_list(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    if request.method == 'GET':
        parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
        parcelles_serializers = serializers.serialize('json', parcelles)
        return JsonResponse(parcelles_serializers, safe=False)

class ParcellesMapView(TemplateView):

    template_name = "map.html"

    def get_context_data(self, **kwargs):
        """Return the view context data."""
        context = super().get_context_data(**kwargs)
        context["parcelles_coop"] = json.loads(serialize("geojson", Parcelle.objects.all()))
        # parcelles_serializers = serializers.serialize('json', parcelles)
        # context["parcelles"] = json.loads(serialize("geojson", Parcelle.objects.all()))
        return context

class ReceptionView(View):
    def get(self, request, *args, **kwargs):
        cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
        parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
        parcelle_list = []
        for parcelle in parcelles:
        #     sub_category = SubCategories.objects.filter(is_active=1, category_id=category.id)
            parcelle_list.append({"parcelle": parcelle})

        # merchant_users = MerchantUser.objects.filter(auth_user_id__is_active=True)
        especes_plants = Espece.objects.all()
        context = {
            "parcelles": parcelles,
            "especes_plants" : especes_plants,
        }
        return render(self.request, "cooperatives/planting_create.html", context)


class AddPlantingView(View):
    def get(self, request, *args, **kwargs):
        cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
        parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
        parcelle_list = []
        for parcelle in parcelles:
            parcelle_list.append({"parcelle": parcelle})

        # merchant_users = MerchantUser.objects.filter(auth_user_id__is_active=True)
        #activate = "plantings"
        especes = Espece.objects.all()
        # print(especes)
        campagnes = Campagne.objects.all()
        projets = Projet.objects.all()
        plantings = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative)
        context = {
            'cooperative': cooperative,
            "parcelles": parcelles,
            "campagnes" : campagnes,
            "projets" : projets,
            "especes" : especes,
            "plantings" : plantings,
            #"activate": activate
        }
        return render(self.request, "cooperatives/plantings.html", context)

    def post(self, request, *args, **kwargs):
        cooperative = request.POST.get('cooperative')
        date = request.POST.get("date")
        nb_plant_exitant = request.POST.get("nb_plant_exitant")
        plant_recus = request.POST.get("plant_recus")
        # details = request.POST.get("details")
        campagne = request.POST.get("campagne")
        parcelle = request.POST.get("parcelle")
        projet = request.POST.get("projet")
        espece_list = request.POST.get("espece")
        nb_plante_liste = request.POST.getlist("nb_plante[]")

        parcelle_obj = Parcelle.objects.get(code=parcelle)
        campagne_obj = Campagne.objects.get(id=campagne)
        projet_obj = Projet.objects.get(id=projet)
        plant_total_obj = nb_plant_exitant + plant_recus

        planting = Planting(
            parcelle=parcelle_obj,
            campagne=campagne_obj,
            projet=projet_obj,
            nb_plant_exitant=nb_plant_exitant,
            plant_recus=plant_recus,
            date=date,
            # plant_recus = (nb_plant_exitant + plant_recus)
        )
        planting.save()


        # espece_obj = Espece.objects.get(id=espece_list)
        # detail_planting = DetailPlanting(
        #     planting_id=planting,
        #     espece = espece_obj,
        #     nb_plante=nb_plante_liste[i]
        # )
        # detail_planting.save()
        # i = i + 1
        # i = 0
        # # espece_obj = Espece.objects.get(id=espece_list)
        # for e in espece_list:
        #     detail_planting = DetailPlanting(
        #         planting_id=planting,
        #         espece=e,
        #         nb_plante=nb_plante_liste[i]
        #     )
        #     detail_planting.save()
        #     i = i+1
        # return HttpResponse("OK")

# def load_producteurs(request):
#     cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
#     producteurs = Producteur.objects.filter(cooperative_id=cooperative).order_by('nom')
#     parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
#     context = {
#         'producteurs': producteurs,
#         'parcelles': parcelles,
#     }
#     return render(request, 'cooperative/select.html', context)

@login_required(login_url='connexion')
def CoopPlantings(request):
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    # parcelles = cooperative.parcelles_set.all()
    parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
    #print(parcelles)
    especes  = Espece.objects.all()
    activate = "plantings"
    # especes = Espece.objects.all()
    campagnes = Campagne.objects.all()
    projets = Projet.objects.all()
    # plantings = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative)

    # for plant in plantings :
    #     plant.nbplant = DetailPlanting.objects.filter(planting_id = plant.code).aggregate(total=Sum('nb_plante'))['total']
    #     if plant.nbplant is not None:
    #         plant.totale = plant.nbplant + plant.nb_plant_exitant
    #     else:
    #         plant.total = plant.nb_plant_exitant
    #         plant.nbplant = 0

    plantingForm = PlantingForm()

    # print(parcelles)
    context = {
        'cooperative':cooperative,
        'parcelles':parcelles,
        # 'plantings':plantings,
        'campagnes':campagnes,
        'projets':projets,
        'especes': especes,
        'plantingForm':plantingForm,
        "activate": activate,
        'role':role
    }
    return render(request, 'cooperatives/plantings.html', context)

@login_required(login_url='connexion')
def detail_planting(request, code=None):
    activate = "plantings"
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    instance = get_object_or_404(Planting, code=code)
    Details_Planting = DetailPlanting.objects.filter(planting_id=instance)

    Monitorings = Monitoring.objects.filter(planting_id=instance)
    remplacements = RemplacementMonitoring.objects.filter(monitoring__planting_id = instance.code)

    for remp in remplacements :
        remp.mort = MonitoringEspeceremplacement.objects.filter(remplacement_id = remp.code).aggregate(total=Sum('mort'))['total']
        remp.remplacer = MonitoringEspeceremplacement.objects.filter(remplacement_id = remp.code).aggregate(total=Sum('remplacer'))['total']
        #print(remp.mort)

    for monitoring in Monitorings:
        monitoring.responsable = User.objects.get(id = monitoring.user_id)
        try:
            monitoring.remplacer = RemplacementMonitoring.objects.filter(monitoring_id = monitoring.code).latest('code')

        except RemplacementMonitoring.DoesNotExist:
            pass



    monitoringForm = MonitoringForm()
    detailPlantingForm = DetailPlantingForm()

    if request.method == 'POST':

        monitoringForm = MonitoringForm(request.POST, request.FILES)
        detailPlantingForm = DetailPlantingForm(request.POST, request.FILES)

        if monitoringForm.is_valid():
            monitoring = monitoringForm.save(commit=False)
            monitoring.planting_id = instance.code
            monitoring = monitoring.save()
            monitoringForm.save_m2m()

            #print(monitoring)
            messages.success(request, "Enregistrement effectué avec succès")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # return HttpResponse("Enregistrement effectué avec succès")

        elif detailPlantingForm.is_valid():
            detail = detailPlantingForm.save(commit=False)
            detail.planting_id = instance.code
            detail = detail.save()
            print(detail)
            messages.success(request, "Enregistrement effectué avec succès")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # return redirect('cooperatives:suivi_planting', kwargs={'cooperatives:suivi_planting': instance.pk})
            # return HttpResponse("Enregistrement effectué avec succès")
        else:
            pass



    try:
        lastMonitoring = Monitoring.objects.filter(planting_id=instance).latest('code')
        context = {
            'cooperative':cooperative,
            'instance':instance,
            'monitoringForm':monitoringForm,
            'detailPlantingForm':detailPlantingForm,
            'Details_Planting':Details_Planting,
            'Monitorings':Monitorings,
            "activate": activate,
            "lastMonitoring":lastMonitoring,
            "remplacements":remplacements,
            'role':role


         }


    except Monitoring.DoesNotExist:
             context = {
            'cooperative':cooperative,
            'instance':instance,
            'monitoringForm':monitoringForm,
            'detailPlantingForm':detailPlantingForm,
            'Details_Planting':Details_Planting,
            'Monitorings':Monitorings,
            "activate": activate,
            "remplacements":remplacements,
            'role':role


         }

    return render(request, 'cooperatives/detail_planting.html', context)




from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import DetailPlantingFormSet
from .models import Planting


class PlantingList(ListView):
    model = Planting
    template_name = "cooperatives/plantings.html"


# class PlantingCreate(CreateView):
#     model = Planting
#     fields = [
#         "parcelle",
#         "nb_plant_exitant",
#         "plant_recus",
#         "campagne",
#         "projet",
#         "date",
#         "date",
#         "details",
#     ]
#
#
# class PlantingDetailsCreate(CreateView):
#     model = Planting
#     fields = [
#         "parcelle",
#         "nb_plant_exitant",
#         "plant_recus",
#         "campagne",
#         "projet",
#         "date",
#         "date",
#         "details",
#     ]
#     success_url = reverse_lazy('add_planting')
#
#     def get_context_data(self, **kwargs):
#         data = super(PlantingDetailsCreate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['detailsplanting'] = DetailPlantingFormSet(self.request.POST)
#         else:
#             data['detailsplanting'] = DetailPlantingFormSet()
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         detailsplanting = context['detailsplanting']
#         with transaction.atomic():
#             self.object = form.save()
#
#             if detailsplanting.is_valid():
#                 detailsplanting.instance = self.object
#                 detailsplanting.save()
#         return super(PlantingDetailsCreate, self).form_valid(form)


# class ProfileUpdate(UpdateView):
#     model = Profile
#     success_url = '/'
#     fields = ['first_name', 'last_name']
#
#
# class ProfileFamilyMemberUpdate(UpdateView):
#     model = Profile
#     fields = ['first_name', 'last_name']
#     success_url = reverse_lazy('profile-list')
#
#     def get_context_data(self, **kwargs):
#         data = super(ProfileFamilyMemberUpdate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['familymembers'] = FamilyMemberFormSet(self.request.POST, instance=self.object)
#         else:
#             data['familymembers'] = FamilyMemberFormSet(instance=self.object)
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         familymembers = context['familymembers']
#         with transaction.atomic():
#             self.object = form.save()
#
#             if familymembers.is_valid():
#                 familymembers.instance = self.object
#                 familymembers.save()
#         return super(ProfileFamilyMemberUpdate, self).form_valid(form)


# class PlantingDelete(DeleteView):
#     model = Planting
#     success_url = reverse_lazy('add_planting')


def folium_map(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)

    m = folium.Map(
        location=[5.34939, -4.01705],
        zoom_start=6
    )
    marker_cluster = MarkerCluster().add_to(m)

    map1 = raster_layers.TileLayer(tiles="CartoDB Dark_Matter").add_to(m)
    map2 = raster_layers.TileLayer(tiles="CartoDB Positron").add_to(m)
    map3 = raster_layers.TileLayer(tiles="Stamen Terrain").add_to(m)
    map4 = raster_layers.TileLayer(tiles="Stamen Toner").add_to(m)
    map5 = raster_layers.TileLayer(tiles="Stamen Watercolor").add_to(m)
    folium.LayerControl().add_to(m)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    df = read_frame(parcelles,
                        fieldnames=
                        [
                            'code',
                            'producteur',
                            'sous_section',
                            'acquisition',
                            'latitude',
                            'longitude',
                            'superficie',
                            'culture',
                            'certification',
                        ]
                    )
    # print(df)
    for (index, row) in df.iterrows():
        folium.Marker(
            location=[
                row.loc['latitude'],
                row.loc['longitude']
            ],
           # my_string='CODE: {}, PRODUCTEUR: {}, SECTION: {}, CERTIFICATION: {}, CULTURE: {}, SUPERFICIE: {}'.format(code,),
            # Popup(my_string),
            popup=[
                row.loc['code'],
                row.loc['producteur'],
                row.loc['certification'],
                row.loc['superficie'],
                row.loc['culture'],
                # 'producteur',
                # 'code',
                # 'certification',
                # 'culture',
                # 'superficie',
                # 'CODE' : 'code',
                # 'PRODUCTUER' : 'producteur',
                # 'SOUS SECTION' : 'sous_section',
                # 'CERTIFICATION' : 'certification',
                # 'CULTURE' : 'culture',
                # 'SUPERFICIE' : 'superficie',
            ],
            icon=folium.Icon(color="green", icon="ok-sign"),
        ).add_to(marker_cluster)
    plugins.Fullscreen().add_to(m)
    plugins.DualMap().add_to(m)
    # plugins.MarkerCluster.add_to()
    m = m._repr_html_()

    context = {
        "m":m
    }
    return render(request, "cooperatives/folium_map.html", context)

def folium_palntings_map(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    m = folium.Map(
        location=[5.34939, -4.01705],zoom_start=6,
    )
    marker_cluster = MarkerCluster().add_to(m)

    map1 = raster_layers.TileLayer(tiles="CartoDB Dark_Matter").add_to(m)
    map2 = raster_layers.TileLayer(tiles="CartoDB Positron").add_to(m)
    map3 = raster_layers.TileLayer(tiles="Stamen Terrain").add_to(m)
    map4 = raster_layers.TileLayer(tiles="Stamen Toner").add_to(m)
    map5 = raster_layers.TileLayer(tiles="Stamen Watercolor").add_to(m)
    folium.LayerControl().add_to(m)
    plantings = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative)
    parcelles = Parcelle.objects.filter(roducteur__cooperative_id=cooperative)

    df1 = read_frame(parcelles,
        fieldnames=
        [
            'code',
            'producteur',
            'latitude',
            'longitude',

        ]
    )
    df = read_frame(plantings,
        fieldnames=
        [
            'planting',
            'espece',
            'nb_plante',
            'add_le'
        ]
    )
    print(df)
    html = df.to_html(
        classes="table table-striped table-hover table-condensed table-responsive"
    )

    # print(df)
    for (index, row) in df1.iterrows():
        folium.Marker(
            location=[
                row.loc['latitude'],
                row.loc['longitude']
            ],
            popup=folium.Popup(html),
            icon=folium.Icon(color="green", icon="ok-sign"),
        ).add_to(marker_cluster)
    plugins.Fullscreen().add_to(m)
    m = m._repr_html_()

    context = {
        "m":m
    }
    return render(request, "cooperatives/folium_planting_map.html", context)


@api_view(['GET'])
def getParcelleCoop(request, pk=None):
    cooperative = Cooperative.objects.get(id=pk)
    # cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
    serializer = ParcelleSerializer(parcelles, many=False)
    # serializer = CooperativeSerliazer(cooperative, many=False)
    return Response(serializer.data)



#parcelle par cooperative sur la carte

@api_view(['GET'])
def map_by_cooperative(request):
    coop_connect = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    sections  = Section.objects.filter(cooperative_id = coop_connect.id)
    context = {
        "coop_connect":coop_connect,
        "sections": sections
    }

    return render(request, 'cooperatives/usercoop/coop_connect_carte.html',context)


#EN MAINTENANCE
@api_view(['GET'])
def edit_monitoring_view(request,code=None):
    d_date = 1
    monitoring = get_object_or_404(Monitoring, code=code)
    detail_monitoring = get_object_or_404(DetailMonitoring, monitoring_id=code)
    especemonitoring = MonitoringEspece.objects.filter(detailmonitoring_id = detail_monitoring.code)
    monitoringForm = MonitoringForm(request.POST or None, request.FILES or None, instance=monitoring)
    context = {
        "monitoring":monitoring,
        "detail_monitoring":detail_monitoring,
        "monitoringForm": monitoringForm,
        "d_date":d_date,
        "Plantings":especemonitoring
    }

    templateStr = render_to_string("cooperatives/edit_monitoring.html", context)
    return JsonResponse({'templateStr':templateStr,'id':code},safe=False)



@api_view(['POST'])
def edit_monitoring(request):
    monitoring_id = request.POST['monitoring_id']
    detail_monitoring = request.POST['detailmonitoring_id']
    instance = get_object_or_404(Monitoring, code=monitoring_id)


    monitoringForm = MonitoringForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST':
        if monitoringForm.is_valid():
            monitoring = monitoringForm.save(commit=False)
            monitoring.save()
            monitoringForm.save_m2m()

            espece = request.POST.getlist('espece')
            detailplanting = request.POST.getlist('d_planting')
            mort = request.POST.getlist('mort')
            mature = request.POST.getlist('mature')
           #print(espece,detailplanting,mort,mature)

            tot_mature = 0
            tot_mort = 0
            for es,de,mt,mtr in zip(espece,detailplanting,mort,mature):
                MonitoringEspece.objects.create(espece_id = int(es),detailplanting_id = de,mort=int(mt),mature =int(mtr) ,  detailmonitoring_id = detail_monitoring)
                MonitoringEspece.objects.filter(detailmonitoring_id = detail_monitoring).delete()
                tot_mature = tot_mature + int(mtr)
                tot_mort = tot_mort + int(mt)

            monitoring.mature_global = tot_mature
            monitoring.mort_global = tot_mort
            monitoring.save()

            return JsonResponse({"msg": "Modification effectuée avec success","status":200},safe=False)
        else:
            return JsonResponse({"errors":monitoringForm.errors,"danger": "Modification incorrect"},safe=False)

#FIN DE EN MAINTENANCE


@api_view(['GET'])
def prod_update(request,code=None):
    d_date = 1
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    sections = Section.objects.filter(id= 44) | Section.objects.filter(cooperative_id = cooperative)
    instance = get_object_or_404(Producteur, code=code)
    form = EditProdForm(request.POST or None, request.FILES or None, instance=instance)
    context = {
		"instance": instance,
		"form":form,
        "d_date": d_date,
        "sections":sections
	}

    templateStr = render_to_string("cooperatives/prod_edt.html", context)
    return JsonResponse({'templateStr':templateStr,'id':code},safe=False)

@api_view(['POST'])
def edit_productor(request):
    code = request.POST['instance_id']
    instance = get_object_or_404(Producteur, code=code)
    form = EditProdForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            producteur = form.save(commit=False)
            producteur.save()
            return JsonResponse({"msg": "Modification effectuée avec success","status":200,"id": code},safe=False)
        else:
            return JsonResponse({"errors":form.errors,"danger": "Modification incorrect"},safe=False)



@api_view(['GET'])
def edit_formatoin(request,id=None):
    d_date = 1
    instance = get_object_or_404(Formation, id=id)
    form = FormationForm(request.POST or None, request.FILES or None, instance=instance)
    context = {
		"instance": instance,
		"form":form,
        "d_date": d_date
	}

    templateStr = render_to_string("cooperatives/edit_formation.html", context)
    return JsonResponse({'templateStr':templateStr,'id':id},safe=False)

@api_view(['POST'])
def update_formation(request):
    id = request.POST['instance_id']
    instance = get_object_or_404(Formation, id=id)
    form = FormationForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            formation = form.save(commit=False)
            formation.save()
            form.save_m2m()
            return JsonResponse({"msg": "Modification effectuée avec success","status":200,"id": id},safe=False)
        else:
            return JsonResponse({"errors":form.errors,"danger": "Modification incorrect"},safe=False)


@api_view(['GET'])
def edit_parcelle(request, code=None):
    d_date = 1
    instance = get_object_or_404(Parcelle, code=code)
    form = EditParcelleForm(request.POST or None, request.FILES or None, instance=instance)
    context = {
		"instance": instance,
		"form":form,
        "d_date": d_date
	}

    templateStr = render_to_string("cooperatives/parcelle_edit.html", context)
    return JsonResponse({'templateStr':templateStr,'id':code},safe=False)



@api_view(['POST'])
def parcelle_update(request):
    code = request.POST['instance_id']
    instance = get_object_or_404(Parcelle, code=code )
    form = EditParcelleForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            parcelle = form.save(commit=False)
            parcelle.save()
            return JsonResponse({"msg": "Modification effectuée avec success","status":200,"id": code},safe=False)
        else:
            return JsonResponse({"errors":form.errors,"danger": "Modification incorrect"},safe=False)



#def update_section(request, id=None):
#    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
#    instance = get_object_or_404(Section, id=id)
#    form = SectionForm(request.POST or None, request.FILES or None, instance=instance)
#    if form.is_valid():
#        instance = form.save(commit=False)
#        instance.cooperative_id = cooperative.id
#        instance.save()
#        messages.success(request, "Section Modifié Avec Succès", extra_tags='html_safe')
#        return HttpResponseRedirect(reverse('cooperatives:section'))
#    context = {
#        'instance' : instance,
#        'form' : form,
#    }
#    return render(request, "cooperatives/section_edit.html", context)



@api_view(['GET'])
def edit_section(request, id=None):
    d_date = 1
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    instance = get_object_or_404(Section, id=id)
    form = SectionForm(request.POST or None, request.FILES or None, instance=instance)
    context = {
		"instance": instance,
		"form":form,
        "d_date": d_date
	}

    templateStr = render_to_string("cooperatives/section_edit.html", context)
    return JsonResponse({'templateStr':templateStr,'id':id},safe=False)

@api_view(['POST'])
def update_section(request):
    id = request.POST['instance_id']
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    instance = get_object_or_404(Section, id=id)
    form = SectionForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.cooperative_id = cooperative.id
        instance.save()
        return JsonResponse({"msg": "Modification effectuée avec success","status":200,"id": id},safe=False)
    else:
        return JsonResponse({"errors":form.errors,"danger": "Modification incorrect"},safe=False)



def delete_section(request,id=None):
    section = get_object_or_404(Section, id=id)
    section.delete()


@api_view(['GET'])
def edit_sous_section(request, id=None):
    d_date = 1
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    sections = Section.objects.all().filter(cooperative_id=cooperative)
    instance = get_object_or_404(Sous_Section, id=id)
    form = Edit_Sous_SectionForm(request.POST or None, request.FILES or None, instance=instance)

    context = {
        'instance' : instance,
        'form' : form,
        "sections":sections
    }
    templateStr = render_to_string("cooperatives/sous_section_edit.html", context)
    return JsonResponse({'templateStr':templateStr,'id':id},safe=False)


@api_view(['POST'])
def update_sous_section(request):
    id = request.POST['instance_id']
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    instance = get_object_or_404(Sous_Section, id=id)
    form = Edit_Sous_SectionForm(request.POST or None, request.FILES or None, instance=instance)
    #form = SectionForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        s_section = form.save(commit=False)
        s_section.save()
        return JsonResponse({"msg": "Modification effectuée avec success","status":200,"id": id},safe=False)
    else:
        return JsonResponse({"errors":form.errors,"danger": "Modification incorrect"},safe=False)



def delete_sous_section(request,id=None):
    item = get_object_or_404(Sous_Section, id=id)
    item.delete()


def monitoringSave(request):
    #print(request.POST['planting'])
       espece = request.POST.getlist('espece')
       detailplanting = request.POST.getlist('d_planting')
       mort = request.POST.getlist('mort')
       #mature = request.POST.getlist('mature')
       recus = request.POST.getlist('recus')
       #print(detailplanting)

       #tot_mature = 0
       tot_mort = 0
       tot_recus = 0

       for mt,rcu in zip(mort,recus):
           if mt != ''  and rcu != '':
                tot_recus = tot_recus + int(rcu)
                tot_mort = tot_mort + int(mt)
                if int(mt) > int(rcu) :
                    return JsonResponse({"msg": "Attention ! Plants vivant d'une espece supperieur au plants recu","status":400},safe=False)
                    sys.exit(0)
                elif int(mt) < 0:
                    return JsonResponse({"msg": "Attention ! Nombres plants ne doit pas etre inferieur à 0","status":400},safe=False)
                    sys.exit(0)
           else:
               return JsonResponse({"msg": "Attention ! Verifier les champs renseignés","status":400},safe=False)
               sys.exit(0)



       if tot_recus <  tot_mort  :
            return JsonResponse({"msg": "Attention! Total Plants vivant supperieur au plants reçu","status":400},safe=False)
       else :
            monitoringForm = MonitoringForm(request.POST, request.FILES)
            if monitoringForm.is_valid():
               monitoring = monitoringForm.save(commit=False)
               totM ='MNT'
               codex = str(datetime.datetime.now().microsecond)
               monitoring.code = "%s%s" % (codex, totM)
               monitoring.planting_id = request.POST['planting']
               monitoring.user_id = request.user.id
               monitoring.save()
               monitoringForm.save_m2m()


               detailmonitoring = DetailMonitoring()
               totD ='DMT'
               codei = str(datetime.datetime.now().microsecond)
               detailmonitoring.code = "%s%s" % (codei, totD)
               detailmonitoring.monitoring_id = monitoring.code
               detailmonitoring.save()



               if request.POST['remplacer'] !='0':
                    totE ='MTE'
                    for es,de,mt,rcu in zip(espece,detailplanting,mort,recus):
                        codee = str(datetime.datetime.now().microsecond)
                        MonitoringEspece.objects.create(espece_id = int(es),code = "%s%s" % (codee, totE),detailplantingremplacement_id = de,mort=int(rcu) - int(mt),  detailmonitoring_id = detailmonitoring.code)
               else :
                    totE ='MTE'
                    for es,de,mt,rcu in zip(espece,detailplanting,mort,recus):
                        codee = str(datetime.datetime.now().microsecond)
                        MonitoringEspece.objects.create(espece_id = int(es),detailplanting_id = de,mort=int(rcu) - int(mt),code = "%s%s" % (codee, totE),  detailmonitoring_id = detailmonitoring.code)


               monitoring.mort_global = tot_recus - tot_mort
               monitoring.mature_global = tot_mort
               monitoring.save()


               return JsonResponse({"msg": "Monitoring effectué avec succes !","status":200},safe=False)
            else:
               return JsonResponse({"errors":monitoringForm.errors,"danger": "Enregistrement incorrect"},safe=False)



def espece_monitoring_view(request,code=None):
    monitoring = get_object_or_404(Monitoring, code=code)
    detail_monitoring = get_object_or_404(DetailMonitoring, monitoring_id=code)
    especemonitoring = MonitoringEspece.objects.filter(detailmonitoring_id = detail_monitoring.code)
    #print(especemonitoring)
    context = {
        'especemonitorings' : especemonitoring,
        'monitoring' : monitoring
    }

    templateStr = render_to_string("cooperatives/monitoring/especemonitoring.html", context)
    return JsonResponse({'templateStr':templateStr},safe=False)


def plantingSave(request):
    espece = request.POST.getlist('espece')
    nb_plante = request.POST.getlist('nb_plante')
    nb_plant_exitant  = request.POST['nb_plant_exitant']
    code_parc  = request.POST['parcelle']


    if code_parc == "":
        return JsonResponse({"msg": "Veillez renseigner le code parcelle","status":400},safe=False)
        sys.exit(0)


    if len(Parcelle.objects.filter(code=code_parc)) == 0:
        return JsonResponse({"msg": "Cette parcelle n'existe pas","status":400},safe=False)
        sys.exit(0)



    tot_espece = 0

    for nb, es in zip(nb_plante, espece):
        if es == '' or nb == '':
            return JsonResponse({"msg": "Attention ! Verifier les champs renseignés","status":400},safe=False)
            sys.exit(0)
        elif int(nb) <= 0 :
            return JsonResponse({"msg": " Attention ! Nombres plants doivent être superieur à 0 ","status":400},safe=False)
            sys.exit(0)
        else:
            tot_espece = tot_espece + int(nb)



    plantingForm = PlantingForm(request.POST, request.FILES)
    parcelle = Parcelle.objects.get(code=code_parc)

    if plantingForm.is_valid():
        planting = plantingForm.save(commit=False)
        totM ='PLG'
        totP ='DPL'
        codex = str(datetime.datetime.now().microsecond)

        planting.code = "%s%s" % (codex, totM)
        planting.parcelle_id = parcelle.code

        planting.save()

        for es, nb in zip(espece, nb_plante):
            codei = str(datetime.datetime.now().microsecond)
            DetailPlanting.objects.create(espece_id = int(es),nb_plante = int(nb),code = "%s%s" % (codei, totP),  planting_id = planting.code)



        planting.plant_recus = tot_espece
        planting.plant_total = planting.plant_recus + int(nb_plant_exitant)
        planting.save()


        return JsonResponse({"msg": "Planting effectué avec succes !","status":200},safe=False)
    else:
        return JsonResponse({"errors":plantingForm.errors,"danger": "Enregistrement incorrect"},safe=False)



def producteurSave(request):

    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    prodForm = ProdForm(request.POST, request.FILES)
    #print(prodForm)
    if prodForm.is_valid():
        producteur = prodForm.save(commit=False)
        producteur.cooperative_id = cooperative.id
        producteur.user_id = request.user.id
        producteur = producteur.save()
            # print(producteur)
        return JsonResponse({"msg": "Enregistrement effectué avec succes !","status":200},safe=False)
    else:
        return JsonResponse({"errors":prodForm.errors,"danger": "Enregistrement incorrect"},safe=False)



def parcelleSave(request):
    parcelleForm = ParcelleForm(request.POST, request.FILES)
    prod = request.POST['producteur']

    if prod == "":
        return JsonResponse({"msg": "Veillez renseigner le code proprietaire","status":400},safe=False)
        sys.exit(0)


    if len(Producteur.objects.filter(code=prod)) == 0:
        return JsonResponse({"msg": "Ce code ne correspond pas a un proprietaire","status":400},safe=False)
        sys.exit(0)


    producteur = Producteur.objects.get(code=prod)

    if Parcelle.objects.filter(producteur_id = producteur.code) and len(Parcelle.objects.filter(producteur_id = producteur.code)) >= producteur.nb_parcelle:
        return JsonResponse({"msg": "Vous ne pouvez plus enregistrer de parcelle pour ce producteur","status":400},safe=False)
        sys.exit(0)


    if parcelleForm.is_valid():
        parcelle = parcelleForm.save(commit=False)
        parcelle.producteur_id = producteur.code
        parcelle.user_id = request.user.id
        if len(Parcelle.objects.filter(producteur_id = producteur.code)) >= 0 :
            tot ='P0'+str(len(Parcelle.objects.filter(producteur_id = producteur.code)) + 1)
            parcelle.code = "%s%s" % (producteur.code, tot)

        parcelle = parcelle.save()
        return JsonResponse({"msg": "Enregistrement effectué avec succes !","status":200},safe=False)
    else:
        return JsonResponse({"errors":parcelleForm.errors,"danger": "Enregistrement incorrect"},safe=False)



############################ formations 1000 #################################################################
@login_required(login_url='connexion')
def tranning(request,id=None):
    activate = "formations"
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    producteurs = Producteur.objects.filter(cooperative_id=cooperative)
    campagnes = Campagne.objects.all()
    participants = Participantcoop.objects.filter(cooperative_id = cooperative)
    intitule = Intitule_Formation.objects.get(id=id)



    formationForm = FormationForm()
    participantForm = ParticipantcoopForm()



    context = {
        "producteurs":producteurs,
        "campagnes":campagnes,
        "formationForm":formationForm,
        "participantForm":participantForm,
        "activate": activate,
        "participants": participants,
        "intitule":intitule,
        'role':role
    }

    return render(request, 'cooperatives/formations/insert.html', context)


def saveParticipant(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)

    participantForm = ParticipantcoopForm(request.POST or None, request.FILES or None)
    nom = request.POST['nom']
    #print(nom)
    if participantForm.is_valid():
        participant = participantForm.save(commit=False)
        participant.cooperative_id = cooperative.id
        participant.nom = nom
        participant = participant.save()
        return JsonResponse({"msg": "Enregistrement effectué avec succes !","status":200},safe=False)
    else:
        return JsonResponse({"errors":participantForm.errors,"danger": "Enregistrement incorrect"},safe=False)



def deletes(request):
    d = request.POST['d']
    run = QueryDict(d,mutable=True)
    print(run.dict())
    #for i in d :
    #    if i != '':
    #        print(i)
            #item = get_object_or_404(Participantcoop, id=int(i))
            #item.delete()




def participant_delete(request,id=None):
    item = get_object_or_404(Participantcoop, id=id)
    item.delete()


def formationSave(request):

    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)

    nom = request.POST.getlist('nom')
    contact = request.POST.getlist('contact')
    #localite = request.POST.getlist('localite')
    parts = request.POST.getlist('participant')

    #print(nom,contact,localite,parts)

    formationForm = FormationForm(request.POST or None, request.FILES or None)
    if formationForm.is_valid():
       formation = formationForm.save(commit=False)
       formation.cooperative_id = cooperative.id
       formation.save()
       formationForm.save_m2m()


       participants = Participantformation.objects.filter(formation_id = formation.id)
       #print(participants)

       for n,cnt,participant in zip(nom,contact,participants):
            participant.nom = n
            participant.contact = cnt
            participant.save()


       for p in parts:
            del_participantscoop = Participantcoop.objects.filter(id = int(p))
            del_participantscoop.delete()


       return JsonResponse({"msg": "Formation enregistrer avec succes !","id":request.POST['intitule'],"status":200},safe=False)
    else:
        return JsonResponse({"errors":formationForm.errors,"danger": "Enregistrement incorrect"},safe=False)




@login_required(login_url='connexion')
def export_formation_to_pdf(request, id=None):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    formation = get_object_or_404(Formation, id=id)
    nb_participant = Participantformation.objects.filter(formation_id = formation.id).count()
    participants = Participantformation.objects.filter(formation_id = id)
    producteurs = Producteur.objects.filter(cooperative_id=cooperative)
    #details = Detail_Formation.objects.filter(formation_id=instance)
    template_path = 'cooperatives/formations/pdf/formation_pdf.html'
    context = {
        'cooperative':cooperative,
        'formation':formation,
        'participants':participants,
        'nb_participant':nb_participant,
        "producteurs":producteurs
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Formation.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy viewp
    if pisa_status.err:
        return HttpResponse('Une Erreure est Survenue, Réessayer SVP...' + html + '</pre>')
    return response


def changeSection(request):

    id = request.POST['id']

    templateStr = '  <option selected value="">-- Select --</option> '

    if id != '':
        s_section = Sous_Section.objects.filter(section_id = id)
        for sect in s_section :
            templateStr =  ' <option value="'+str(sect.id)+'">'+ sect.libelle +'  </option>'


    return JsonResponse({'templateStr':templateStr,'id':id},safe=False)



@api_view(['POST'])
def contactProd(request):
    nom = request.POST['nom']

    producteur = Producteur.objects.get(nom__exact = nom)
   #print(producteur.contacts)
    if producteur:
        return JsonResponse({'contact':producteur.contacts},safe=False)
    else:
        pass


############################remplacement 1000#################################################################
def remplacement_monitoring_view(request,code):
    monitoring = get_object_or_404(Monitoring, code=code)
    detail_monitoring = get_object_or_404(DetailMonitoring, monitoring_id=code)
    especemonitoring = MonitoringEspece.objects.filter(detailmonitoring_id = detail_monitoring.code)
    especes_plants = Espece.objects.all()
    formRemplacement = RemplacementMonitoringForm()
    context = {
        'especes' : especemonitoring,
        'monitoringremplaces' : monitoring,
        'especes_plants': especes_plants,
        'formRemplacement':formRemplacement
    }
    templateStr = render_to_string("cooperatives/monitoring/monitoringremplace.html", context)
    return JsonResponse({'templateStr':templateStr},safe=False)



def RemplaceSave(request):

    espece = request.POST.getlist('espece')
    mort = request.POST.getlist('mort')
    remplacer = request.POST.getlist('remplacer')
    recus = request.POST.getlist('recus')
    newrecus = request.POST.getlist('newrecus')
    newespece = request.POST.getlist('newespece')
    mortn = request.POST.getlist('mortn')
    remplacern = request.POST.getlist('remplacern')
    #print(espece,mort,remplacer,recus,newrecus,newespece,mortn,remplacern)

    tot_mort = 0
    tot_remplacer = 0
    tot_recus = 0
    tot_new = 0
    tot_mortn = 0
    tot_remplacern = 0

    for es,m,rp,rc in zip(espece,mort,remplacer,recus):
        if rc == '0':
            m =0

        if rp != '' :
            tot_mort = tot_mort + int(m)
            tot_remplacer = tot_remplacer + int(rp)
            tot_recus = tot_recus + int(rc)
            if int(rp) > int(m) :
                    return JsonResponse({"msg": "Attention ! Plants de remplacement d'une espèce supérieur au plants morts","status":400},safe=False)
                    sys.exit(0)
            elif int(rp)< 0:
                return JsonResponse({"msg": "Attention ! Nombres plants ne doit pas être inférieur à 0","status":400},safe=False)
                sys.exit(0)
        else:
            return JsonResponse({"msg": "Attention ! Verifier les champs renseignés","status":400},safe=False)
            sys.exit(0)

    monitoring = get_object_or_404(Monitoring, code=request.POST['monitoring'])
    planting = get_object_or_404(Planting, code=monitoring.planting.code)

    date = request.POST['date']

    remplacementM = RemplacementMonitoring()
    remplacementM.date = date
    totR = 'RMT'
    codes = str(datetime.datetime.now().microsecond)
    remplacementM.code = "%s%s" % (codes, totR)
    remplacementM.monitoring_id = monitoring.code
    remplacementM.save()

    totD = 'DPR'


    for es,m,rp,rc in zip(espece,mort,remplacer,recus):
        codex = str(datetime.datetime.now().microsecond)
        DetailPlantingRemplacement.objects.create(espece_id = int(es),nb_plante = int(rc),code = "%s%s" % (codex, totD),planting_id = planting.code,remplacer_id = remplacementM.code)



    for  mtn,rpn,nw,nes in zip(mortn,remplacern,newrecus,newespece):
        tot_mortn = tot_mortn + int(mtn)
        tot_remplacern = tot_remplacern + int(rpn)
        tot_new = tot_new + int(nw)
        if nes == "" and nw:
            pass
        elif nes != "" and nw :
            codex = str(datetime.datetime.now().microsecond)
            DetailPlantingRemplacement.objects.create(espece_id = int(nes),nb_plante = int(nw),code = "%s%s" % (codex, totD),planting_id = planting.code,remplacer_id = remplacementM.code)



    planting.plant_recus = tot_recus + tot_new
    planting.save()

    totM = 'MER'

        #print(planting.plant_recus)


    for es,m,rp,rc in zip(espece,mort,remplacer,recus):
        if rc == '0':
            m = 0
        coder = str(datetime.datetime.now().microsecond)
        MonitoringEspeceremplacement.objects.create(espece_id = int(es),remplacer = int(rp),code = "%s%s" % (coder, totM),mort=int(m),futur = int(m)-int(rp), recu = int(rc),remplacement_id= remplacementM.code)



    for nes,nrc in zip(newespece,newrecus):
        if nes == "" and nrc:
            pass
        elif nes != "" and nrc :
            coder = str(datetime.datetime.now().microsecond)
            MonitoringEspeceremplacement.objects.create(espece_id = int(nes),remplacer = 0,code = "%s%s" % (coder, totM),mort=0,futur=0,  recu = int(nrc),remplacement_id= remplacementM.code)




    monitoring.mort_global = tot_mort - tot_remplacer
    monitoring.mature_global =  monitoring.mature_global + tot_remplacer
    monitoring.save()


    return JsonResponse({"msg": "Remplacement effectué avec succes!","status":300},safe=False)



@api_view(['POST'])
def endremplaceSave(request):
    data = request.POST['data']
    run = QueryDict(data,mutable=True)
     #runs = list(run.items())
    espece = run.pop('espece')
    mort = run.pop('mort')
    remplacer = run.pop('remplacer')
    recus = run.pop('recus')
    newrecus = run.pop('newrecus')
    newespece = run.pop('newespece')
    mortn = run.pop('mortn')
    remplacern =run.pop('remplacern')

    tot_mort = 0
    tot_remplacer = 0
    tot_recus = 0
    tot_new = 0
    tot_mortn = 0
    tot_remplacern = 0


    for es,m,rp,rc in zip(espece,mort,remplacer,recus):
        if rc == '0':
            m =0

        if rp != '' :
            tot_mort = tot_mort + int(m)
            tot_remplacer = tot_remplacer + int(rp)
            tot_recus = tot_recus + int(rc)
            if int(rp) > int(m) :
                    return JsonResponse({"msg": "Attention ! Plants de remplacement d'une espèce supperieur au plants morts","status":400},safe=False)
                    sys.exit(0)
            elif int(rp)< 0:
                return JsonResponse({"msg": "Attention ! Nombres plants ne doit pas être inférieur à 0","status":400},safe=False)
                sys.exit(0)
        else:
            return JsonResponse({"msg": "Attention ! Verifier les champs renseignés","status":400},safe=False)
            sys.exit(0)


    for moni in run.pop('monitoring'):
         monitoring = get_object_or_404(Monitoring, id=int(moni))

    for d in run.pop('date'):
         date = d

    planting = get_object_or_404(Planting, id=monitoring.planting.id)

    remplacementM = RemplacementMonitoring()
    remplacementM.date = date
    remplacementM.monitoring_id = monitoring.id
    remplacementM.save()



    for es,m,rp,rc in zip(espece,mort,remplacer,recus):
        DetailPlantingRemplacement.objects.create(espece_id = int(es),nb_plante = int(rc),planting_id = planting.id,remplacer_id = remplacementM.id)



    for  mtn,rpn,nw,nes in zip(mortn,remplacern,newrecus,newespece):
        tot_mortn = tot_mortn + int(mtn)
        tot_remplacern = tot_remplacern + int(rpn)
        tot_new = tot_new + int(nw)
        if nes == "" and nw:
            pass
        elif nes != "" and nw :
            DetailPlantingRemplacement.objects.create(espece_id = int(nes),nb_plante = int(nw),planting_id = planting.id,remplacer_id = remplacementM.id)


    planting.plant_recus = tot_recus + tot_new
    planting.save()


    #print(planting)
    #print(run.pop('monitoring'),run.pop('mort'))



    for m,es,rc,rp in zip(mort,espece,recus,remplacer):
        if rc == '0':
            m = 0

        MonitoringEspeceremplacement.objects.create(espece_id = int(es),remplacer = int(rp),mort=int(m),futur = int(m)-int(rp), recu = int(rc),remplacement_id= remplacementM.id)


    for nes,nrc in zip(newespece,newrecus):
        if nes == "" and nrc:
            pass
        elif nes != "" and nrc :
            MonitoringEspeceremplacement.objects.create(espece_id = int(nes),remplacer = 0,mort=0,futur=0,recu = int(nrc),remplacement_id= remplacementM.id)




    monitoring.mort_global = tot_mort - tot_remplacer
    monitoring.mature_global =  monitoring.mature_global + tot_remplacer
    monitoring.save()





def esrempla_monitoring_view(request,code=None):
    remplace = RemplacementMonitoring.objects.get(code=code)
    especemonitoring = MonitoringEspeceremplacement.objects.filter(remplacement_id = code)
    #print(especemonitoring)
    context = {
        'especemonitorings' : especemonitoring,
        'remplace' : remplace
    }
    templateStr = render_to_string("cooperatives/monitoring/esremplacer.html", context)
    return JsonResponse({'templateStr':templateStr},safe=False)




def rempend_monitoring_view(request,code=None):
    remplace = RemplacementMonitoring.objects.get(code=code)
    especemonitoring = MonitoringEspeceremplacement.objects.filter(remplacement_id = code)
    especes_plants = Espece.objects.all()
    formRemplacement = RemplacementMonitoringForm()
    #print(especemonitoring)
    context = {
        'especes' : especemonitoring,
        'especes_plants': especes_plants,
        'formRemplacement':formRemplacement,
        'remplace':remplace
    }
    templateStr = render_to_string("cooperatives/monitoring/aftermoni_espece.html", context)
    return JsonResponse({'templateStr':templateStr},safe=False)


def monitoring_form_view(request,code=None):


    try:
        monitoring = Monitoring.objects.filter(planting_id = code).latest('-code')
        #remplacer = RemplacementMonitoring.objects.filter(monitoring_id = monitoring.id).latest('id')
        rmp = len(RemplacementMonitoring.objects.filter(monitoring_id= monitoring.code))
        if rmp > 0 :
            # print(monitoring.code)
            instance = get_object_or_404(Planting, code=code)
            remplacer = RemplacementMonitoring.objects.filter(monitoring_id = monitoring.code).latest('-code')
            remplmonitoringViews = DetailPlantingRemplacement.objects.filter(planting_id=instance.code , remplacer_id=remplacer.code )
            monitoringForm = MonitoringForm()
            context = {
            "remplacer":remplacer,
            'instance' : instance,
            'monitoringForm' : monitoringForm,
            "remplmonitoringViews" : remplmonitoringViews
            }
            templateStr = render_to_string("cooperatives/monitoring/form_monitoringrplace.html", context)
            return JsonResponse({'templateStr':templateStr,'id':code},safe=False)
        elif rmp == 0 :
            monitorings = Monitoring.objects.filter(planting_id = code).order_by('-code')

            for moni in monitorings :

                if len(RemplacementMonitoring.objects.filter(monitoring_id= moni.code)) > 0:
                    inst = get_object_or_404(Planting, code=code)
                    rempla = RemplacementMonitoring.objects.filter(monitoring_id =  moni.code).latest('code')
                    remplmonitoringViews = DetailPlantingRemplacement.objects.filter(planting_id=inst.code , remplacer_id=rempla.code )
                    monitoringForm = MonitoringForm()
                    context = {
                    "remplacer":rempla,
                    'instance' : inst,
                    'monitoringForm' : monitoringForm,
                    "remplmonitoringViews" : remplmonitoringViews
                    }
                    templateStr = render_to_string("cooperatives/monitoring/form_monitoringrplace.html", context)
                    return JsonResponse({'templateStr':templateStr,'id':code},safe=False)
                    sys.exit(0)
                else :
                    instance = get_object_or_404(Planting, code=code)
                    remplmonitoringViews = DetailPlanting.objects.filter(planting_id=instance)
                    monitoringForm = MonitoringForm()
                    context = {
                    'instance' : instance,
                    'monitoringForm' : monitoringForm,
                    "remplmonitoringViews" : remplmonitoringViews
                    }
                    templateStr = render_to_string("cooperatives/monitoring/form_monitoring.html", context)
                    return JsonResponse({'templateStr':templateStr,'id':code},safe=False)


    except Monitoring.DoesNotExist :
        instance = get_object_or_404(Planting, code=code)
        remplmonitoringViews = DetailPlanting.objects.filter(planting_id=instance)
        monitoringForm = MonitoringForm()
        context = {
        'instance' : instance,
        'monitoringForm' : monitoringForm,
        "remplmonitoringViews" : remplmonitoringViews
        }
        templateStr = render_to_string("cooperatives/monitoring/form_monitoring.html", context)
        return JsonResponse({'templateStr':templateStr,'id':code},safe=False)


##plus pris en compte#####
def deleteEspece(request, id=None):
    item = get_object_or_404(MonitoringEspece, id=id)
    item.delete()

    return JsonResponse({'id':id},safe=False)


############################remplacement 1000#################################################################

@login_required(login_url='connexion')
def production(request):
    activate = "productions"
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    productions = Production.objects.filter(parcelle__producteur__cooperative_id=cooperative)
    form = ProductionForm()
    if request.method == 'POST':
        form = ProductionForm(request.POST, request.FILES)
        if form.is_valid():
            production = ProductionForm.save(commit=False)
            for parcelle in parcelles.iterator():
                production.parcelle_id = parcelle.id
                production.save()
                # print(production)
        messages.success(request, "Production Ajoutée avec succès")
        return HttpResponseRedirect(reverse('cooperatives:productions'))
    context = {
        "cooperative":cooperative,
        "parcelles": parcelles,
        "productions": productions,
        'form': form,
        'role':role
    }
    return render(request, "cooperatives/productions/productions.html", context)


def productionSave(request):
    parc = request.POST['parcelles']
    qty = request.POST['qteProduct']
    form = ProductionForm(request.POST, request.FILES)

    if parc == "":
        return JsonResponse({"msg": "Veillez renseigner le code parcelle","status":400},safe=False)
        sys.exit(0)


    if len(Parcelle.objects.filter(code=parc)) == 0:
        return JsonResponse({"msg": "Ce code ne correspond pas a une parcelle ","status":400},safe=False)
        sys.exit(0)


    parcelle = Parcelle.objects.get(code=parc)
    maxkgv1 = parcelle.superficie * 800

    if len(Production.objects.filter(parcelle = parcelle.code)) == 0 :
         if int(qty) > int(maxkgv1):
            return JsonResponse({"msg": "La capacitée de production en kg de cette parcelle est atteinte ","status":400},safe=False)
            sys.exit(0)
    elif len(Production.objects.filter(parcelle = parcelle.code)) == 1 :
        production = Production.objects.get(parcelle = parcelle.code)
        sommeKg = 0
        sommeKg = production.qteProduct + int(qty)

        if sommeKg > int(maxkgv1):
            return JsonResponse({"msg": "La capacitée de production en kilogramme ("+str(round(maxkgv1,1))+"kg)  de cette parcelle est atteinte" ,"status":400},safe=False)
            sys.exit(0)

    elif len(Production.objects.filter(parcelle = parcelle.code)) > 1 :
        productions1 = Production.objects.filter(parcelle = parcelle)
        sommeKg = 0

        for prod in productions1 :
            sommeKg = sommeKg + prod.qteProduct


        if sommeKg > int(maxkgv1):
            return JsonResponse({"msg": "La capacitée de production en kilogramme ("+str(round(maxkgv1,1))+"kg)  de cette parcelle est atteinte" ,"status":400},safe=False)
            sys.exit(0)



    if form.is_valid():
        product = form.save(commit=False)
        totP = 'PDT'
        coder = str(datetime.datetime.now().microsecond)
        product.code = "%s%s" % (coder,totP)
        product.parcelle_id = parcelle.code
        product = product.save()
        return JsonResponse({"msg": "Enregistrement effectué avec succes !","status":200},safe=False)
    else:
        return JsonResponse({"errors":form.errors,"danger": "Enregistrement incorrect"},safe=False)



    #print(sommeKg)



@api_view(['GET'])
def edit_product(request, code=None):
    instance = get_object_or_404(Production, code=code)
    form = EditProductionForm(request.POST or None, request.FILES or None, instance=instance)
    context = {
		"instance": instance,
		"form":form,
	}

    templateStr = render_to_string("cooperatives/productions/product_edit.html", context)
    return JsonResponse({'templateStr':templateStr,'id':code},safe=False)



@api_view(['POST'])
def production_update(request):
    code = request.POST['instance_id']
    qty = request.POST['qteProduct']
    parcelle_id = request.POST['parcelle']
    instance = get_object_or_404(Production, code=code)
    form = EditProductionForm(request.POST or None, request.FILES or None, instance=instance)

    parcelle = Parcelle.objects.get(code=parcelle_id)
    maxkgv1 = parcelle.superficie * 800

    if len(Production.objects.filter(parcelle = parcelle.code)) == 0 :
         if int(qty) > int(maxkgv1):
            return JsonResponse({"msg": "La capacitée de production en kg de cette parcelle est atteinte ","status":400},safe=False)
            sys.exit(0)
    elif len(Production.objects.filter(parcelle = parcelle.code)) == 1 :
        production = Production.objects.get(parcelle = parcelle.code)
        sommeKg = 0
        sommeKg = production.qteProduct + int(qty)

        if sommeKg > int(maxkgv1):
            return JsonResponse({"msg": "La capacitée de production en kilogramme ("+str(round(maxkgv1,1))+"kg)  de cette parcelle est atteinte" ,"status":400},safe=False)
            sys.exit(0)

    elif len(Production.objects.filter(parcelle = parcelle.code)) > 1 :
        productions1 = Production.objects.filter(parcelle = parcelle)
        sommeKg = 0

        for prod in productions1 :
            sommeKg = sommeKg + prod.qteProduct


        if sommeKg > int(maxkgv1):
            return JsonResponse({"msg": "La capacitée de production en kilogramme ("+str(round(maxkgv1,1))+"kg)  de cette parcelle est atteinte" ,"status":400},safe=False)
            sys.exit(0)


    if request.method == 'POST':
        if form.is_valid():
            parcelle = form.save(commit=False)
            parcelle.save()
            return JsonResponse({"msg": "Modification effectuée avec success","status":200,"id": code},safe=False)
        else:
            return JsonResponse({"errors":form.errors,"danger": "Modification incorrect"},safe=False)





def production_delete(request,code=None):
    production = get_object_or_404(Production, code=code)
    production.delete()





############ SECTION DES API-SERVER FLUTTER #############################################

@api_view(['GET'])
def getProducteursForcoop(request,id):
    # cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    producteurs = Producteur.objects.filter(cooperative_id=id)
    serializers = ProducteurSerializer(producteurs,many = True)
    return Response(serializers.data)

@api_view(['GET'])
def getMonitoringForcoop(request):
    monitoring = Monitoring.objects.all()
    serializers = MonitoringSerializer(monitoring,many = True)
    return Response(serializers.data)



@api_view(['POST'])
def createProducteurs(request):
    # cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    data = request.data
    if len(Producteur.objects.filter(code=data['code'])) == 0 :
        producteur = Producteur.objects.create(
            code = data['code'],
            origine_id = int(data['origine_id']),
            cooperative_id = int(data['cooperative_id']),
            sous_prefecture_id = data['sous_prefecture_id'],
            type_producteur = data['type_producteur'],
            nom = data['nom'],
            dob = datetime.datetime.fromisoformat(data['dob']),
            genre = data['genre'],
            contacts = data['contacts'],
            localite =  data['localite'],
            section_id = int(data['section_id']),
            sous_section_id = data['sous_section_id'],
            nb_parcelle = int(data['nb_parcelle']),
            image = data['image'],
            type_document = data['type_document'],
            num_document = data['num_document'],
            document = data['document'],
            nb_enfant = int(data['nb_enfant']),
            nb_epouse = int(data['nb_epouse']),
            enfant_scolarise = int(data['enfant_scolarise']),
            nb_personne = int(data['nb_personne']),
            user_id = int(data['user_id']),
        )
        serializer = ProducteurSerializer(producteur, many= False)

        histosync = SyncHistorique()
        histosync.date = datetime.datetime.now()
        histosync.cooperative_id = int(data['cooperative_id'])
        histosync.user_id = int(data['user_id'])
        histosync.indice = 'PROD'
        histosync.save()


        return Response(serializer.data)
    else:
        product = get_object_or_404(Producteur, code=data['code'])
        product.nom = data['nom']
        product.contacts = data['contacts']
        product.localite = data['localite']
        product.section_id = int(data['section_id'])
        product.nb_parcelle = int(data['nb_parcelle'])
        product.nb_enfant = int(data['nb_enfant'])
        product.nb_epouse = int(data['nb_epouse'])
        product.enfant_scolarise = int(data['enfant_scolarise'])
        product.user_id = int(data['user_id'])
        product.save()

#

@api_view(['PUT'])
def updateProducteur(request,code):
    data = request.data
    producteur = Producteur.objects.get(code = code)
    serializer = ProducteurSerializer(producteur, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)



#parcelleAPI
@api_view(['GET'])
def getListParcForcoop(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    parcelle = Parcelle.objects.filter(producteur__cooperative_id= cooperative)
    serializer = ParcelleSerializer(parcelle, many= True)
    return Response(serializer.data)


@api_view(['POST'])
def createParcelle(request):
    data = request.data
    if len(Parcelle.objects.filter(code=data['code'])) == 0 :
        parcelle = Parcelle.objects.create(
            code = data['code'],
            producteur_id = data['producteur_id'],
            acquisition = data['acquisition'],
            latitude = data['latitude'],
            longitude = data['longitude'],
            culture = data['culture'],
            type_parcelle = data['type_parcelle'],
            certification = data['certification'],
            superficie = float(data['superficie']),
            code_certificat = data['code_certificat'],
            annee_certificat = data['annee_certificat'],
            annee_acquis = data['annee_acquis'],
            projet_id =int(data['projet_id']),
            user_id = int(data['user_id']),
        )
        histosync = SyncHistorique()
        histosync.date = datetime.datetime.now()
        histosync.cooperative_id = int(data['cooperative_id'])
        histosync.user_id = int(data['user_id'])
        histosync.indice = 'PARC'
        histosync.save()

        serializer = ParcelleSerializer(parcelle, many= False)
        return Response(serializer.data)
    else:
        parcelle = get_object_or_404(Parcelle, code=data['code'])
        parcelle.code = data['code'],
        parcelle.acquisition = data['acquisition'],
        parcelle.latitude = data['latitude'],
        parcelle.longitude = data['longitude'],
        parcelle.culture = data['culture'],
        type_parcelle = data['type_parcelle'],
        parcelle.certification = data['certification'],
        parcelle.superficie = float(data['superficie']),
        parcelle.code_certificat = data['code_certificat'],
        parcelle.annee_certificat = data['annee_certificat'],
        parcelle.annee_acquis = data['annee_acquis'],
        parcelle.projet_id =int(data['projet_id']),
        parcelle.user_id = int(data['user_id']),

        parcelle.save()


@api_view(['POST'])
def createPlanting(request):
    data = request.data
    op = Planting.objects.filter(code=data['code'])
    length = len(op)
    if length == 0 :
        planting = Planting.objects.create(
            code = data['code'],
            campagne_id = int(data['campagne_id']),
            parcelle_id = data['parcelle_id'],
            nb_plant_exitant = int(data['nb_plant_exitant']),
            plant_recus = 0,
            plant_total = 0,
            user_id = int(data['user_id']),
            date = datetime.datetime.fromisoformat(data['date'])
        )
        serializer = PlantingSerializer(planting, many=False)

        histosync = SyncHistorique()
        histosync.date = datetime.datetime.now()
        histosync.cooperative_id = int(data['cooperative_id'])
        histosync.user_id = int(data['user_id'])
        histosync.indice = 'PLAN'
        histosync.save()

        return Response(serializer.data)
    else:
        pass



@api_view(['PUT'])
def updatePlanting(request,code):
    dataup = request.data
    planting= Planting.objects.get(code=code)
    serial = PlantingSerializer(planting, data = dataup)
    # print(serial)
    if serial.is_valid(raise_exception=True):
        print('good')
        serial.save()

    return Response(serial.data)


@api_view(['POST'])
def createDetailplanting(request):
    data = request.data
    if len(DetailPlanting.objects.filter(code=data['code'])) == 0 :
        detailplanting = DetailPlanting.objects.create(
            code = data['code'],
            planting_id = data['planting_id'],
            espece_id = int(data['espece_id']),
            nb_plante = int(data['nb_plante']),
            # unik = data['unik']
        )
        planting = get_object_or_404(Planting, code=data['planting_id'])
        planting.plant_recus = planting.plant_recus + int(data['nb_plante'])
        planting.save()

        histosync = SyncHistorique()
        histosync.date = datetime.datetime.now()
        histosync.cooperative_id = int(data['cooperative_id'])
        histosync.user_id = int(data['user_id'])
        histosync.indice = 'DEPL'
        histosync.save()
        serializer = DetailsPlantingSerializer(detailplanting, many=False)
        return Response(serializer.data)
    else :
        detail = get_object_or_404(DetailPlanting, code=data['code'])
        planting = get_object_or_404(Planting, code=data['planting_id'])

        planting.plant_recus = (planting.plant_recus - detail.nb_plante) + int(data['nb_plante'])
        planting.save()
        detail.espece_id = int(data['espece_id'])
        detail.nb_plante = int(data['nb_plante'])
        detail.save()


##api monitoring
@api_view(['POST'])
def monitoringCreate(request):
    data = request.data
    if len(Monitoring.objects.filter(code=data['code'])) == 0 :
        if request.method == 'POST':
            monitoring = Monitoring.objects.create(
                code = data['code'],
                planting_id = data['planting_id'],
                mort_global = int(data['mort_global']),
                mature_global = int(data['mature_global']),
                date = datetime.datetime.fromisoformat(data['date']),
                user_id = int(data['user_id']),
            )
            histosync = SyncHistorique()
            histosync.date = datetime.datetime.now()
            histosync.cooperative_id = int(data['cooperative_id'])
            histosync.user_id = int(data['user_id'])
            histosync.indice = 'MNT'
            histosync.save()
            serializer = MonitoringSerializer(monitoring, many=False)
            return Response(serializer.data)
    else:
        moni = get_object_or_404(Monitoring, code = data['code'])
        moni.mort_global = int(data['mort_global'])
        moni.mature_global = int(data['mature_global'])
        moni.date = datetime.datetime.fromisoformat(data['date'])
        moni.user_id = int(data['user_id'])
        moni.save()



@api_view(['PUT'])
def updateMonitoring(request,code):
        dataup = request.data
        monitoring= Monitoring.objects.get(code=code)
        serial = MonitoringSerializer(monitoring, data = dataup)
        if serial.is_valid(raise_exception=True):
            serial.save()

        print('oops')
        return Response(serial.data)


@api_view(['POST'])
def createDetailmonitoring(request):
    data = request.data
    detailmonitoring = DetailMonitoring.objects.create(
        code = data['code'],
        monitoring_id = data['monitoring_id'],
        user_id = int(data['user_id'])
    )
    histosync = SyncHistorique()
    histosync.date = datetime.datetime.now()
    histosync.cooperative_id = int(data['cooperative_id'])
    histosync.user_id = int(data['user_id'])
    histosync.indice = 'DMT'
    histosync.save()
    serializer = DetailMonitoringSerializer(detailmonitoring, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def obsMonitoringFunc(request):
    data = request.data
    observation = MonitoringObsMobile.objects.create(
        monitoring_id = data['monitoring_id'],
        observation_id = int(data['obsmonitoring_id']),
        user_id = int(data['user_id'])
    )

    histosync = SyncHistorique()
    histosync.date = datetime.datetime.now()
    histosync.cooperative_id = int(data['cooperative_id'])
    histosync.user_id = int(data['user_id'])
    histosync.indice = 'OBM'
    histosync.save()
    serializer = MonitoringObservationSerializer(observation, many=False)
    return Response(serializer.data)



@api_view(['POST'])
def createEspecemonitoring(request):
    data = request.data
    if len(MonitoringEspece.objects.filter(code = data['code'])) == 0:
        if request.method == "POST":
            especemonitoring = MonitoringEspece.objects.create(
                code = data['code'],
                detailmonitoring_id = data['detailmonitoring_id'],
                espece_id = int(data['espece_id']),
                detailplanting_id = data['detailplanting_id'],
                mort = int(data['mort']),
                # detailplantingremplacement_id = data['detailplantingremplacement'],
                # taux_mortalite = data['taux_mortalite'],
            )

            histosync = SyncHistorique()
            histosync.date = datetime.datetime.now()
            histosync.cooperative_id = int(data['cooperative_id'])
            histosync.user_id = int(data['user_id'])
            histosync.indice = 'MOE'
            histosync.save()
            serializer = MonitoringEspeceSerializer(especemonitoring, many=False)
            return Response(serializer.data)
    else:
        especeMoni = get_object_or_404(MonitoringEspece, code = data['code'])
        especeMoni.mort = int(data['mort'])
        especeMoni.user_id = int(data['user_id'])
        especeMoni.save()

##########################28/06/2022################MPI###################HISTORIQUE#############

@login_required(login_url='connexion')
def view_historique(request):
    activate = "historique"
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    utilisatuer = Utilisateur()
    historiques = SyncHistorique.objects.filter(cooperative_id = cooperative.id).values('date','user__username','user__id','user__last_name','user__first_name').distinct().annotate(ind=Count('indice'))

    syncUser = []
    User = cooperative.utilisateur.all()
    for s in User :
        if str(s.role) == 'technicien' :
            syncUser.append(s)



    context = {
        'cooperative': cooperative,
        'activate': activate,
        'role':role,
        'syncUser':syncUser,
        'historiques':historiques,
    }
    return render(request, 'historique/histoPage.html', context)


def consult_histo(request):
    id = request.GET.get('id')
    date = request.GET.get('date')
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    prodint = 0
    parcint = 0
    planint = 0
    deplint = 0
    # historiques = SyncHistorique.objects.filter(cooperative_id = cooperative.id).values('date','user__username','user__id','user__last_name','user__first_name').distinct().annotate(ind=Count('indice'))
    prod = SyncHistorique.objects.filter(cooperative_id = cooperative.id).filter(indice = 'PROD').filter(date=date,user_id  = int(id)).values('indice').annotate(ind=Count('indice'))
    parc = SyncHistorique.objects.filter(cooperative_id = cooperative.id).filter(indice = 'PARC').filter(date=date,user_id  = int(id)).values('indice').annotate(ind=Count('indice'))
    plan = SyncHistorique.objects.filter(cooperative_id = cooperative.id).filter(indice = 'PLAN').filter(date=date,user_id  = int(id)).values('indice').annotate(ind=Count('indice'))
    depl = SyncHistorique.objects.filter(cooperative_id = cooperative.id).filter(indice = 'DEPL').filter(date=date,user_id  = int(id)).values('indice').annotate(ind=Count('indice'))

    for p in prod :
        prodint = p['ind']


    for pa in parc :
        parcint = pa['ind']


    for pl in plan :
        planint = pl['ind']


    for de in depl :
        deplint = de['ind']


    context = {
        'prod':prodint,
        'parc':parcint,
        'plan':planint,
        'depl':deplint,
        'date':date
	}

    templateStr = render_to_string("historique/consult_view.html", context)
    return JsonResponse({'templateStr':templateStr,'date':date,'id':id},safe=False)



###importation de ficher producteur

@login_required(login_url='connexion')
def saveProdFile(request):
    role = Role.objects.get(id = request.user.utilisateur.role_id)
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    if request.method == "POST" and request.FILES['prodFile'] : 
        prodFile = request.FILES['prodFile']
        
        if not prodFile.name.endswith('xlsx') |  prodFile.name.endswith('xls') | prodFile.name.endswith('csv') | prodFile.name.endswith('ods')  : 
            messages.info(request, 'mauvais format')
            return redirect('cooperatives:producteurs')
        else :
            fs = FileSystemStorage()
            filename = fs.save(prodFile.name, prodFile)
            upload_url = fs.url(filename)
            exceldata = pd.read_excel(filename)
            
            if set(['code','nom','localite','section','nb_parcelle','genre','date_naissance','contact']).issubset(exceldata.columns) :
                
                for db in exceldata.itertuples() : 
                    if exceldata.isnull().values.any() != True  :
                            if len(ImportProdFileModel.objects.filter(code = db.code).filter(cooperative_id = cooperative.id)) == 0 :
                                if len(Producteur.objects.filter(code=db.code)) == 0 :
                                    objdata = ImportProdFileModel.objects.create(
                                        code = db.code.upper(),
                                        nom = db.nom.upper(),
                                        localite = db.localite,
                                        section_id = int(db.section),
                                        nb_parcelle = db.nb_parcelle,
                                        genre = db.genre,
                                        dob = db.date_naissance,
                                        contacts = db.contact,
                                        user_id = request.user.utilisateur.id,
                                        cooperative_id = cooperative.id,
                                    )
                                else :
                                     producteur = get_object_or_404(Producteur,code = db.code)
                                     objdata = ImportProdFileModel.objects.create(
                                        code = producteur.code,
                                        nom = producteur.nom,
                                        localite = producteur.localite,
                                        section_id = producteur.section_id,
                                        nb_parcelle = producteur.nb_parcelle,
                                        genre = producteur.genre,
                                        dob = producteur.dob,
                                        contacts = producteur.contacts,
                                        user_id = request.user.utilisateur.id,
                                        cooperative_id = cooperative.id,
                                        nom_prime = db.nom.upper(),
                                        localite_prime=db.localite,
                                        section_prime = db.section,
                                        nb_parcelle_prime = db.nb_parcelle,
                                        genre_prime = db.genre,
                                        dob_prime = db.date_naissance,
                                        contacts_prime = db.contact,
                                        user_id_prime = request.user.utilisateur.id,
                                        cooperative_prime= cooperative.id
                                    )
                            
                            elif len(ImportProdFileModel.objects.filter(code = db.code).filter(cooperative_id = cooperative.id).filter(etatValidate = "EN ATTENTE")) >0 :
                                prod = get_object_or_404(ImportProdFileModel,code = db.code)
                                prod.nom_prime = db.nom.upper()
                                prod.localite_prime=db.localite
                                prod.section_prime = db.section
                                prod.nb_parcelle_prime = db.nb_parcelle
                                prod.genre_prime = db.genre
                                prod.dob_prime = db.date_naissance
                                prod.contacts_prime = db.contact
                                prod.etatValidate = "EN ATTENTE"
                                prod.user_id_prime = request.user.utilisateur.id
                                prod.cooperative_prime= cooperative.id
                                
                                
                                prod.save()
                            elif len(ImportProdFileModel.objects.filter(code = db.code).filter(cooperative_id = cooperative.id).filter(etatValidate = "ANNULER")) > 0 or len(ImportProdFileModel.objects.filter(code = db.code).filter(cooperative_id = cooperative.id).filter(etatValidate = "IMPORTER")) > 0 :
                                if len(Producteur.objects.filter(code=db.code)) > 0 :
                                    prod = get_object_or_404(ImportProdFileModel,code = db.code)
                                    prod.nom_prime = db.nom.upper()
                                    prod.localite_prime=db.localite
                                    prod.section_prime = db.section
                                    prod.nb_parcelle_prime = db.nb_parcelle
                                    prod.genre_prime = db.genre
                                    prod.dob_prime = db.date_naissance
                                    prod.contacts_prime = db.contact
                                    prod.etatValidate = "EN ATTENTE"
                                    prod.user_id_prime = request.user.utilisateur.id
                                    prod.cooperative_prime= cooperative.id
                                    prod.save()
                                else :
                                    prod = get_object_or_404(ImportProdFileModel,code = db.code)
                                    prod.delete()
                                    objdata = ImportProdFileModel.objects.create(
                                        code = db.code.upper(),
                                        nom = db.nom.upper(),
                                        localite = db.localite,
                                        section_id = int(db.section),
                                        nb_parcelle = db.nb_parcelle,
                                        genre = db.genre,
                                        dob = db.date_naissance,
                                        contacts = db.contact,
                                        user_id = request.user.utilisateur.id,
                                        cooperative_id = cooperative.id,
                                    )
                        
                     
                    else :
                         messages.info(request, 'Erreur les columns [code,nom,section,cooperative]  ont une ou plusieurs cases vide')
                         return redirect('cooperatives:producteurs')
            else : 
                messages.info(request, 'Erreur dans sur les columns de votre fichier [code,nom,localite,section,cooperative,nb_parcelle,genre,date_naissance,contact]')
                return redirect('cooperatives:producteurs')
                        

        listProd = ImportProdFileModel.objects.filter(etatValidate = "EN ATTENTE").filter(cooperative_id = cooperative.id)
        #filename = fs.save(prodFile.name, prodFile)
        filedel = fs.delete(prodFile.name)

        context = {
            'cooperative': cooperative,
            'role':role,
            'listProd':listProd
        }
        return render(request, 'historique/test.html',context)
    
@api_view(['GET'])
def importValidProd(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    ficherAimporter = ImportProdFileModel.objects.filter(etatValidate = "EN ATTENTE").filter(cooperative_id = cooperative.id)

    for fichierprod in ficherAimporter:
        
        if fichierprod.nom_prime is not None :
            if len(Producteur.objects.filter(code=fichierprod.code)) == 0 :
                prod = Producteur.objects.create(
                    code = fichierprod.code,
                    cooperative_id = fichierprod.cooperative_prime,
                    origine_id = 1,
                    sous_prefecture_id = 1,
                    nom = fichierprod.nom_prime,
                    dob  = fichierprod.dob_prime,
                    genre = fichierprod.genre_prime,
                    contacts = fichierprod.contacts_prime,
                    localite = fichierprod.localite_prime,
                    section_id = fichierprod.section_prime,
                    nb_parcelle = fichierprod.nb_parcelle_prime,
                    user_id = fichierprod.user_id_prime
                )
            else:
                producteur =get_object_or_404(Producteur, code=fichierprod.code)
                producteur.cooperative_id = fichierprod.cooperative_prime
                producteur.nom = fichierprod.nom_prime
                producteur.dob  = fichierprod.dob_prime
                producteur.genre = fichierprod.genre_prime
                producteur.contacts = fichierprod.contacts_prime
                producteur.localite = fichierprod.localite_prime
                producteur.section_id = int(fichierprod.section_prime)
                producteur.nb_parcelle = fichierprod.nb_parcelle_prime
                producteur.user_id = fichierprod.user_id_prime
                
                producteur.save()
                
        else :
            if len(Producteur.objects.filter(code=fichierprod.code)) == 0 :
                prod = Producteur.objects.create(
                        code = fichierprod.code,
                        cooperative_id = fichierprod.cooperative_id,
                        origine_id = 1,
                        sous_prefecture_id = 1,
                        nom = fichierprod.nom,
                        dob  = fichierprod.dob,
                        genre = fichierprod.genre,
                        contacts = fichierprod.contacts,
                        localite = fichierprod.localite,
                        section_id = fichierprod.section_id,
                        nb_parcelle = fichierprod.nb_parcelle,
                        user_id = fichierprod.user_id
                    )
            else :
                producteur =get_object_or_404(Producteur, code=fichierprod.code)
                producteur.cooperative_id = fichierprod.cooperative_id
                producteur.nom = fichierprod.nom
                producteur.dob  = fichierprod.dob
                producteur.genre = fichierprod.genre
                producteur.contacts = fichierprod.contacts
                producteur.localite = fichierprod.localite
                producteur.section_id = int(fichierprod.section_id)
                producteur.nb_parcelle = fichierprod.nb_parcelle
                producteur.user_id = fichierprod.user_id
                
                producteur.save()
        
        fichierprod.etatValidate = "IMPORTER"
        fichierprod.save()
                  
    #return redirect('cooperatives:producteurs')
            
        
@api_view(['GET'])
def importAnnuleProd(request):
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    ficherAimporter = ImportProdFileModel.objects.filter(etatValidate = "EN ATTENTE").filter(cooperative_id = cooperative.id)
    
    for fichierprod in ficherAimporter :
        fichierprod.etatValidate = "ANNULER"
        fichierprod.save()
        

### datatable ################################################################
@api_view(['POST'])
def prodTableFunction(request):
    draw = request.POST['draw']
    row = request.POST['start']
    rowperpage = request.POST['length']
    columIndex = request.POST['order[0][column]']
    columnName = request.POST['columns['+columIndex+'][data]']
    columnSortOrder = request.POST['order[0][dir]']
    searchValue = request.POST['search[value]']
    
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    arrayProd = []

    #recherche = Producteur.objects.raw("SELECT count(*) as allcount FROM cooperatives_producteur WHERE code LIKE %s OR nom LIKE %s OR genre LIKE %s OR type_producteur LIKE %s OR section %s OR localite LIKE %s",(likeString,likeString,likeString,likeString,likeString,likeString))
    prodLong = Producteur.objects.filter(cooperative_id=cooperative)
    recherche = Producteur.objects.filter(cooperative_id=cooperative).filter(Q(code__contains = searchValue)
                                                                             |Q(nom__contains = searchValue)
                                                                             |Q(genre__contains = searchValue)
                                                                             |Q(type_producteur__contains = searchValue)
                                                                             |Q(section__libelle__contains = searchValue)
                                                                             |Q(localite__contains = searchValue)
                                                                             )
    
    if searchValue == "":
        # producteurs = Producteur.objects.filter(cooperative_id=cooperative).order_by(columnName)[:int(row)].values()
        producteurs = Producteur.objects.filter(cooperative_id=cooperative).order_by("-created_at")[int(row):int(row)+int(rowperpage)]
        for prod in producteurs :
           
            item = {
                # "image": prod.image.url,
                "code":prod.code,
                "nom":prod.nom,
                "genre":prod.genre,
                "type_producteur":prod.type_producteur,
                "section_libelle":Section.objects.get(id= prod.section_id).libelle,
                "localite":prod.localite,
                "action": '<a href="#" onclick="edit_prod(\'{0}\')" style="padding: 3px;margin-top: 6px;margin-right:5px;" class="btn btn-primary"><i class="fa fa-edit fa-fw"></i></a><a href="#" onclick="delete_semence(\'{1}\')" style="padding: 3px;margin-top: 6px;" class="btn btn-danger"><i class="fa fa-trash fa-fw"></i></a>'.format(
                        reverse('cooperatives:modifier', args=[prod.code]),
                        reverse('cooperatives:del_producteur', args=[prod.code])
                    )
                }
            arrayProd.append(item)
    else:
        producteurs = Producteur.objects.filter(cooperative_id=cooperative).filter(Q(code__contains = searchValue)
                                                                             |Q(nom__contains = searchValue)
                                                                             |Q(genre__contains = searchValue)
                                                                             |Q(type_producteur__contains = searchValue)
                                                                             |Q(section__libelle__contains = searchValue)
                                                                             |Q(localite__contains = searchValue)
                                                                             ).order_by("-created_at")[int(row):int(row)+int(rowperpage)]
        # producteurs = Producteur.objects.filter(cooperative_id=cooperative).filter(code__istartswith =searchValue).order_by(columnName)[int(row):int(rowperpage)].values()
        for prod in producteurs :
            item = {
                # "image": prod.image.url,
                "code":prod.code,
                "nom":prod.nom,
                "genre":prod.genre,
                "type_producteur":prod.type_producteur,
                "section_libelle":Section.objects.get(id= prod.section_id).libelle,
                "localite":prod.localite,
                "action": '<a href="#" onclick="edit_prod(\'{0}\')" style="padding: 3px;margin-top: 6px; margin-right:5px;" class="btn btn-primary"><i class="fa fa-edit fa-fw"></i></a><a href="#" onclick="delete_semence(\'{1}\')" style="padding: 3px;margin-top: 6px;" class="btn btn-danger"><i class="fa fa-trash fa-fw"></i></a>'.format(
                    reverse('cooperatives:modifier', args=[prod.code]),
                    reverse('cooperatives:del_producteur', args=[prod.code])
                    )
                 }
            arrayProd.append(item)
        
    
    return JsonResponse({
            'draw':int(draw),
            'recordsTotal' : len(prodLong),
            'recordsFiltered':len(recherche),
            'aaData': arrayProd,
            },safe=False)
    
    

        
    
    
@api_view(['POST'])
def parcTableFunction(request):
    draw = request.POST['draw']
    row = request.POST['start']
    rowperpage = request.POST['length']
    columIndex = request.POST['order[0][column]']
    columnName = request.POST['columns['+columIndex+'][data]']
    columnSortOrder = request.POST['order[0][dir]']
    searchValue = request.POST['search[value]']
    
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    arrayParc = []
    
    
    parcLong = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
    recherche = Parcelle.objects.filter(producteur__cooperative_id=cooperative).filter(Q(code__contains = searchValue)
                                                                                       |Q(producteur__nom__contains = searchValue)
                                                                                       |Q(producteur__section__libelle__contains = searchValue)
                                                                                       |Q(culture__contains = searchValue)
                                                                                       |Q(superficie__contains = searchValue)
                                                                                       |Q(longitude__contains = searchValue)
                                                                                       |Q(latitude__contains = searchValue)
                                                                                       )
    
    
    if searchValue == "":
        
        parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative).order_by('-created_at')[int(row):int(row)+int(rowperpage)]
        for par in parcelles :
            item = {
                "code":par.code,
                "producteur":par.producteur.nom,
                "section":par.producteur.section.libelle,
                "culture":par.culture,
                "superficie":par.superficie,
                "longitude":par.longitude,
                "latitude":par.latitude,
                "action": '<a href="#" onclick="edit_parcelle(\'{0}\')" style="padding: 3px;margin-top: 6px; margin-right:5px;" class="btn btn-primary"><i class="fa fa-edit fa-fw"></i></a><a href="#" onclick="delete_semence(\'{1}\')" style="padding: 3px;margin-top: 6px;" class="btn btn-danger"><i class="fa fa-trash fa-fw"></i></a>'.format(
                    reverse('cooperatives:edit_parcelle', args=[par.code]),
                    reverse('cooperatives:parcelle_delete', args=[par.code])
                    )
            }
            arrayParc.append(item)
    else:
        parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative).filter(Q(code__contains = searchValue)
                                                                                       |Q(producteur__nom__contains = searchValue)
                                                                                       |Q(producteur__section__libelle__contains = searchValue)
                                                                                       |Q(culture__contains = searchValue)
                                                                                       |Q(superficie__contains = searchValue)
                                                                                       |Q(longitude__contains = searchValue)
                                                                                       |Q(latitude__contains = searchValue)
                                                                                       ).order_by('-created_at')[int(row):int(row)+int(rowperpage)]
        # parcelles = Parcelle.objects.filter(Q(producteur__cooperative_id= cooperative.id, code__istartswith=searchValue) | Q(producteur__nom__istartswith = searchValue)  | Q(culture__istartswith = searchValue) | Q(superficie__istartswith = searchValue) | Q(longitude__istartswith = searchValue)| Q(latitude__istartswith = searchValue)).order_by(columnName)[:int(rowperpage)]
        for par in parcelles :
            item = {
                "code":par.code,
                "producteur":par.producteur.nom,
                "section":par.producteur.section.libelle,
                "culture":par.culture,
                "superficie":par.superficie,
                "longitude":par.longitude,
                "latitude":par.latitude,
                "action": '<a href="#" onclick="edit_parcelle(\'{0}\')" style="padding: 3px;margin-top: 6px; margin-right:5px;" class="btn btn-primary"><i class="fa fa-edit fa-fw"></i></a><a href="#" onclick="delete_semence(\'{1}\')" style="padding: 3px;margin-top: 6px;" class="btn btn-danger"><i class="fa fa-trash fa-fw"></i></a>'.format(
                    reverse('cooperatives:edit_parcelle', args=[par.code]),
                    reverse('cooperatives:parcelle_delete', args=[par.code])
                    )
            }
            arrayParc.append(item)
            
    
    
    return JsonResponse({
            'draw':int(draw),
            'recordsTotal' : len(parcLong),
            'recordsFiltered':len(recherche),
            'aaData': arrayParc,
            },safe=False)
    

@api_view(['POST'])
def plantTableFunction(request):
    draw = request.POST['draw']
    row = request.POST['start']
    rowperpage = request.POST['length']
    columIndex = request.POST['order[0][column]']
    columnName = request.POST['columns['+columIndex+'][data]']
    columnSortOrder = request.POST['order[0][dir]']
    searchValue = request.POST['search[value]']
    
    cooperative = Cooperative.objects.get(utilisateur=request.user.utilisateur)
    arrayPlant = []
    
    plantLong = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative)
    recherche = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(Q(parcelle__producteur__nom__contains = searchValue)
                                                                                                 |Q(parcelle__code__contains = searchValue)
                                                                                                 |Q(date__contains = searchValue)
                                                                                                 |Q(nb_plant_exitant__contains = searchValue)
                                                                                                 ) 

    if searchValue == "":
        plantings = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).order_by('-created_at')[int(row):int(row)+int(rowperpage)]
        
        for plant in plantings :
            nbplant = DetailPlanting.objects.filter(planting_id = plant.code).aggregate(total=Sum('nb_plante'))['total']
            if nbplant is not None :
                item = {
                    "producteur" : plant.parcelle.producteur.nom,
                    "parcelle" : plant.parcelle.code,
                    "existant" : plant.nb_plant_exitant,
                    "recus" : nbplant,
                    "total" : nbplant + plant.nb_plant_exitant,
                    "date" : plant.date,
                    "action" : '<a href="{0}" class="btn btn-success">suivi <i class="fa fa-chevron-right"></i></a>'.format(
                        reverse('cooperatives:suivi_planting', args=[plant.code]),
                    )
                    
                }
                
                arrayPlant.append(item)
                
    else:

        plantings = Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(Q(parcelle__producteur__nom__contains = searchValue)
                                                                                                 |Q(parcelle__code__contains = searchValue)
                                                                                                 |Q(date__contains = searchValue)
                                                                                                 |Q(nb_plant_exitant__contains = searchValue)
                                                                                                 ).order_by('-created_at')[int(row):int(row)+int(rowperpage)]
        for plant in plantings :
            nbplant = DetailPlanting.objects.filter(planting_id = plant.code).aggregate(total=Sum('nb_plante'))['total']
            if nbplant is not None :
                item = {
                    "producteur" : plant.parcelle.producteur.nom,
                    "parcelle" : plant.parcelle.code,
                    "existant" : plant.nb_plant_exitant,
                    "recus" : nbplant,
                    "total" : nbplant + plant.nb_plant_exitant,
                    "date" : plant.date,
                    "action" : '<a href="{0}" class="btn btn-success">suivi <i class="fa fa-chevron-right"></i></a>'.format(
                        reverse('cooperatives:suivi_planting', args=[plant.code]),
                    )
                    
                }
                
                arrayPlant.append(item)
    
                
                
    
    return JsonResponse({
            'draw':int(draw),
            'recordsTotal' : len(plantLong),
            'recordsFiltered':len(recherche),
            'aaData': arrayPlant,
            },safe=False)
    
                