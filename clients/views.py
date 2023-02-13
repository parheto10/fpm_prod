import os
from itertools import product
import datetime
from xmlrpc.client import DateTime
import xlwt
from django.db.models import Count
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as dj_login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.staticfiles import finders
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.template.loader import get_template
from django.urls import reverse
# from django.utils.encoding import force_text
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.template.loader import render_to_string
# from twisted.words.protocols.jabber.jstrports import client
#from xhtml2pdf import pisa
from xhtml2pdf import pisa
from django.db.models import Q

from parametres.forms import PepiniereForm
from .models import Client
from parametres.models import (
    Sous_Prefecture,
    Origine,
    Prime,
    Projet,
    Activite,
    Region,
    Campagne, Cooperative, Pepiniere, Espece
)

from cooperatives.models import (
    Monitoring,
    MonitoringEspeceremplacement,
    Participantformation,
    Producteur,
    Parcelle,
    Planting,
    RemplacementMonitoring,
    Section,
    Sous_Section, Formation, Detail_Formation, DetailPlanting, Production
)


@login_required(login_url='connexion')
def client_index(request):
    cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
    production = 0
    petite_production = 0
    grande_production = 0
    nb_cooperatives = 0
    nb_parcelles = 0
    Superficie = 0
    nb_producteurs = 0
    Total_plant = 0

    for cooperative in cooperatives :

        if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total']) != None:
            production = production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total'])

        if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total']) != None :
            petite_production = petite_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total'])

        if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total']) != None :
            grande_production = grande_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total'])

        AllCooperatives = Cooperative.objects.filter(id = cooperative.id)
        nb_producteurs = nb_producteurs + Producteur.objects.filter(cooperative_id=cooperative.id).count()
        prod_coop = Cooperative.objects.filter(id = cooperative.id).annotate(nb_producteur=Count('producteurs'))
        nb_cooperatives = nb_cooperatives + Cooperative.objects.filter(id = cooperative.id).count()
        section_coop = Cooperative.objects.filter(id = cooperative.id).annotate(nb_section=Count('sections'))
        nb_parcelles = nb_parcelles + Parcelle.objects.filter(producteur__cooperative=cooperative).count()
        if Parcelle.objects.filter(producteur__cooperative=cooperative).aggregate(total=Sum('superficie'))['total'] != None :
            Superficie = Superficie + Parcelle.objects.filter(producteur__cooperative=cooperative).aggregate(total=Sum('superficie'))['total']

        if Planting.objects.filter(parcelle__producteur__cooperative=cooperative).aggregate(total=Sum('plant_recus'))['total'] != None :
           Total_plant = Total_plant + Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('plant_recus'))['total']



    production = production /1000
    petite_production = petite_production /1000
    grande_production = grande_production /1000





 
    if len(cooperatives) > 1 :
        for coop in cooperatives:
            coop.parcelles =  Parcelle.objects.filter(producteur__cooperative=coop).count()
            coop.productions = Production.objects.filter(parcelle__producteur__cooperative=coop).aggregate(total=Sum('qteProduct'))['total']
            coop.plants = Planting.objects.filter(parcelle__producteur__cooperative=coop).aggregate(total=Sum('plant_recus'))['total']
            if Parcelle.objects.filter(producteur__cooperative=coop).aggregate(total=Sum('superficie'))[ 'total'] != None :
                coop.superficies = int(Parcelle.objects.filter(producteur__cooperative=coop).aggregate(total=Sum('superficie'))[ 'total'])

    elif len(cooperatives) == 1 :
        coop = cooperatives[0]
        coop.parcelles = Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).count()
        coop.productions = Production.objects.filter(parcelle__producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('qteProduct'))['total']
        coop.plants = Planting.objects.filter(parcelle__producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('plant_recus'))['total']
        if Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('superficie'))[ 'total'] != None:
            coop.superficies = int(Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('superficie'))[ 'total'])


    ANNEES = []
    for r in range(2019, (datetime.datetime.now().year+1)):
        ANNEES.append(r)

    context = {
        'cooperatives': cooperatives,
        'AllCooperatives': AllCooperatives,
        'nb_cooperatives': nb_cooperatives,
        'nb_producteurs': nb_producteurs,
        'nb_parcelles': nb_parcelles,
        'Superficie': Superficie,
        'Total_plant': Total_plant,
        'prod_coop': prod_coop,
        'section_coop': section_coop,
        'production': production,
        'petite_production': petite_production,
        'grande_production': grande_production,
        'annee':ANNEES
        # 'activate': activate
        # 'section_cooperative': section_cooperative,
    }
    return render(request, 'clients/index.html', context)


@login_required(login_url='connexion')
def detail_coop(request, id=None):
    activate = "dashboard"
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_nb_producteurs =
    section = Section.objects.filter(cooperative_id=cooperative)
    sous_sections = Sous_Section.objects.filter(section__cooperative_id=cooperative)
    # section_prod = Producteur.objects.all().filter(section_id__in=section).count()
    section_prod = Section.objects.annotate(nb_producteur=Count('producteurs'))
    prod_section = Producteur.objects.filter(section_id__in=section).count()
    coop_nb_producteurs = Producteur.objects.filter(cooperative_id=cooperative).count()
    nb_formations = Formation.objects.filter(cooperative_id=cooperative).count()
    parcelles_section = Parcelle.objects.filter(producteur__section_id__in=section).count()
    # section_parcelle = Section.objects.annotate(nb_producteur=Count('producteurs.parcelles'))
    coop_nb_parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative).count()
    coop_superficie = Parcelle.objects.filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
    section_superf = Parcelle.objects.filter(producteur__section_id__in=section).aggregate(total=Sum('superficie'))['total']
    coop_plants_total = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).aggregate( total=Sum('nb_plante'))['total']

    production = 0
    petite_production = 0
    grande_production = 0

    if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total']) != None:
        production = production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total'])

    if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total']) != None :
        petite_production = petite_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total'])

    if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total']) != None :
        grande_production = grande_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total'])

    production = production /1000
    petite_production = petite_production /1000
    grande_production = grande_production /1000

    context = {
        'cooperative': cooperative,
        'coop_nb_producteurs': coop_nb_producteurs,
        'coop_nb_parcelles': coop_nb_parcelles,
        'coop_superficie': coop_superficie,
        'nb_formations': nb_formations,
        'section': section,
        'sous_sections': sous_sections,
        'prod_section': prod_section,
        'section_prod': section_prod,
        # 'section_parcelle': section_parcelle,
        'parcelles_section': parcelles_section,
        'coop_plants_total': coop_plants_total,
        'section_superf': section_superf,
        'production': production,
        'petite_production': petite_production,
        'grande_production': grande_production,
        'activate': activate
        # 'labels': labels,
        # 'data': data,
    }
    return render(request, 'clients/Coop/cooperative.html', context)

# @login_required(login_url='connexion')
# def detail_coop(request, id=None):
#     activate = "dashboard"
#     cooperative = get_object_or_404(Cooperative, id=id)
#     # coop_nb_producteurs =
#     section = Section.objects.filter(cooperative_id=cooperative)
#     sous_sections = Sous_Section.objects.filter(section__cooperative_id=cooperative)
#     # section_prod = Producteur.objects.all().filter(section_id__in=section).count()
#     section_prod = Section.objects.annotate(nb_producteur=Count('producteurs'))
#     prod_section = Producteur.objects.filter(section_id__in=section).count()
#     coop_nb_producteurs = Producteur.objects.filter(cooperative_id=cooperative).count()
#     nb_formations = Formation.objects.filter(cooperative_id=cooperative).count()
#     parcelles_section = Parcelle.objects.filter(producteur__section_id__in=section).count()
#     # section_parcelle = Section.objects.annotate(nb_producteur=Count('producteurs.parcelles'))
#     coop_nb_parcelles = Parcelle.objects.filter(producteur__section__cooperative_id=cooperative).count()
#     coop_superficie = \
#     Parcelle.objects.filter(producteur__cooperative_id=cooperative).aggregate(total=Sum('superficie'))['total']
#     section_superf = Parcelle.objects.filter(producteur__section_id__in=section).aggregate(total=Sum('superficie'))[
#         'total']
#     # section_plating = Planting.objects.filter(parcelle__producteur__section_id__in=section).aggregate(total=Sum('plant_recus'))['total']
#     # plantings = DetailPlanting.objects.values("espece__libelle").filter(planting__parcelle__producteur__cooperative_id=cooperative).annotate(plante=Sum('plant_recus'))
#     coop_plants_total = \
#     DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).aggregate(
#         total=Sum('nb_plante'))['total']
#
#     context = {
#         'cooperative': cooperative,
#         'coop_nb_producteurs': coop_nb_producteurs,
#         'coop_nb_parcelles': coop_nb_parcelles,
#         'coop_superficie': coop_superficie,
#         'nb_formations': nb_formations,
#         'section': section,
#         'sous_sections': sous_sections,
#         'prod_section': prod_section,
#         'section_prod': section_prod,
#         # 'section_parcelle': section_parcelle,
#         'parcelles_section': parcelles_section,
#         'coop_plants_total': coop_plants_total,
#         'section_superf': section_superf,
#         'activate': activate
#         # 'labels': labels,
#         # 'data': data,
#     }
#     return render(request, 'clients/Coop/cooperative.html', context)


@login_required(login_url='connexion')
def section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sections = Section.objects.all().filter(cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sections': coop_sections,
    }
    return render(request, 'clients/Coop/coop_sections.html', context)


@login_required(login_url='connexion')
def sous_section_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_sous_sections = Sous_Section.objects.all().filter(section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_sous_sections': coop_sous_sections,
    }
    return render(request, 'clients/Coop/coop_sous_sections.html', context)


def prod_coop(request, id=None):
    activate = "producteurs"
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    # coop_parcelles = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_producteurs': coop_producteurs,
        "activate": activate
    }
    return render(request, 'clients/Coop/coop_producteurs.html', context)


@login_required(login_url='connexion')
def parcelle_coop(request, id=None):
    activate = "parcelles"
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    coop_parcelles = Parcelle.objects.filter(producteur__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_parcelles': coop_parcelles,
        'activate': activate
    }
    return render(request, 'clients/Coop/coop_parcelle.html', context)


@login_required(login_url='connexion')
def planting_coop(request, id=None):
    activate = "plantings"
    cooperative = get_object_or_404(Cooperative, id=id)
    coop_plants = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative)
    context = {
        'cooperative': cooperative,
        'coop_plants': coop_plants,
        "activate": activate
    }
    return render(request, 'clients/Coop/coop_plantings.html', context)


@login_required(login_url='connexion')
def projet(request):
    client = Client.objects.get(user_id=request.user.id)
    projets = Projet.objects.all().filter(client_id=client)
    context = {
        'client': client,
        'projets': projets,
    }
    return render(request, 'clients/projets.html', context)

def prod_coop_par_campagne(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    querysets = Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).values("campagne").annotate(qteProduct=Sum('qteProduct'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['campagne'])
        data.append(stat['qteProduct'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

@login_required(login_url='connexion')
def detail_proj(request, id=None):
    instance = get_object_or_404(Projet, id=id)
    # cooperatives = Cooperative.objects.filter(cooperative__projet__i).count()
    producteurs_proj = Producteur.objects.filter(cooperative__projet=instance).count()
    parcelles = Parcelle.objects.filter(producteur__cooperative__projet=instance)
    # parcelles = Planting.objects.all().filter(projet_id=instance)
    nb_parcelles_proj = Parcelle.objects.filter(producteur__cooperative__projet=instance).count()
    plants = DetailPlanting.objects.filter(planting__projet_id=instance).aggregate(total=Sum('nb_plante'))['total']
    # nb_plants_proj = Planting.objects.all().filter(projet_id = instance).count()
    superficie_proj = \
    Parcelle.objects.filter(producteur__cooperative__projet=instance).aggregate(total=Sum('superficie'))['total']

    # print(superficie_proj)
    context = {
        'instance': instance,
        'parcelles': parcelles,
        'plants': plants,
        # 'parcelles':plants,
        'nb_parcelles_proj': nb_parcelles_proj,
        # 'nb_plants_proj':nb_plants_proj,
        # 'plants':plants,
        'superficie_proj': superficie_proj,
        'producteurs_proj': producteurs_proj,
    }
    return render(request, 'clients/projet.html', context)


@login_required(login_url='connexion')
def formations(request, id=None):
    activate = "formations"
    cooperative = get_object_or_404(Cooperative, id=id)
    formations = Formation.objects.filter(cooperative_id=cooperative.id)

    for formation in formations:
        formation.nb_participant = Participantformation.objects.filter(formation_id=formation.id).count()

    context = {
        'cooperative': cooperative,
        'formations': formations,
        "activate": activate

        # 'detailFormation':detailFormation,
        # 'participants': participants,
    }
    return render(request, 'clients/Coop/coop_formations.html', context)


def detail_formation(request, id=None, _id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    formations = Formation.objects.filter(cooperative_id=cooperative.id)

    for formation in formations:
        formation.nb_participant = Participantformation.objects.filter(formation_id=formation.id).count()

    context = {
        'cooperative': cooperative,
        'formations': formations,

        # 'detailFormation':detailFormation,
        # 'participants': participants,
    }
    # print(participants)
    return render(request, 'clients/Coop/detail_formation1.html', context)


def localisation(request):
    parcelles = Parcelle.objects.all()
    context = {
        'parcelles': parcelles
    }
    return render(request, 'clients/carte.html', context)


def localisation_coop(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    # coop_producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    points_coop = Parcelle.objects.all().filter(producteur__section__cooperative_id=cooperative)
    context = {
        'points_coop': points_coop
    }
    return render(request, 'carte1.html', context)


# EXPORT EXCEL
@login_required(login_url='connexion')
def export_prod_xls(request, id=None):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['COOPERATIVE', 'CODE', 'NOM ET PRENOMS', 'SECTION', 'LOCALITE', 'STATUT']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = get_object_or_404(Cooperative, id=id)
    rows = Producteur.objects.all().filter(cooperative_id=cooperative.id).values_list(
        'cooperative__sigle',
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


@login_required(login_url='connexion')
def export_parcelle_xls(request, id=None):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Parcelles.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Parcelles')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['COOPERATIVE', 'CODE', 'PROPRIETAIRE', 'SECTION', 'LOCALITE', 'SUPERFICIE(Ha)', 'LATITUDE', 'LONGITUDE', 'CULTURE']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    cooperative = get_object_or_404(Cooperative, id=id)
    rows = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative.id).values_list(
        'producteur__cooperative__sigle',
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


# EXPORT PDF
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


@login_required(login_url='connexion')
def export_prods_to_pdf(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    producteurs = Producteur.objects.all().filter(cooperative_id=cooperative)
    template_path = 'cooperatives/producteurs_pdf.html'
    context = {
        'cooperative': cooperative,
        'producteurs': producteurs,
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


@login_required(login_url='connexion')
def export_parcelles_to_pdf(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    parcelles = Parcelle.objects.all().filter(producteur__cooperative_id=cooperative)
    template_path = 'cooperatives/new_parcelles_pdf.html'
    context = {
        'cooperative': cooperative,
        'parcelles': parcelles,
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


# Statistiques Charts
def producteur_section(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    section = Section.objects.filter(cooperative_id=cooperative)
    querysets = Producteur.objects.filter(section_id__in=section).values("section__libelle")
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['section__libelle'])
        data.append(stat['qte_recu'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


def Plantings(request):
    querysets = Planting.objects.values("parcelle__producteur__cooperative__sigle").annotate(plant_recus=Sum('plant_recus'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['parcelle__producteur__cooperative__sigle'])
        data.append(stat['plant_recus'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


def DetailPlantings(request):
    # querysets =  DetailPlanting.objects.values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    querysets = []
    cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
    # for cooperative in cooperatives :
    query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id__in=cooperatives).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    for q in query :
        querysets.append(q)


    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })





def coopdetailPlantings(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    querysets = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


def plants_par_section(request, id=None):
    cooperative = get_object_or_404(Cooperative, id=id)
    sections = Section.objects.filter(cooperative_id=cooperative)
    querysets = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).filter(
        planting__parcelle__producteur__section_id__in=sections).values(
        "planting__parcelle__producteur__section__libelle").annotate(nb_plante=Sum('nb_plante'))
    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['planting__parcelle__producteur__section__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

@login_required(login_url='connexion')
def pepiniere(request):
    pepinieres = Pepiniere.objects.all()
    pepiForm = PepiniereForm()
    activate = "pepiniere"
    if request.method == 'POST':
        pepiForm = PepiniereForm(request.POST, request.FILES)
        if pepiForm.is_valid():
            pepiniere = pepiForm.save(commit=False)
            pepiniere = pepiniere.save()
            print(pepiniere)
        messages.success(request, "Site Pépinière Ajouté avec succès")
        # return HttpResponseRedirect(reverse('pepinieres'))

    context = {
        'pepinieres': pepinieres,
        'pepiForm': pepiForm,
        'activate': activate
    }
    return render(request, 'clients/pepinieres.html', context)
# Create your views here.


@login_required(login_url='connexion')
def export_formation_to_pdf(request, id=None):
    formation = get_object_or_404(Formation, id=id)
    cooperative = Cooperative.objects.get(id=formation.cooperative.id)
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

def producteur(request):
    cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
    return render(request, 'clients/producteurs.html')

def parcelle(request):
    return render(request, 'clients/parcelles.html')

def production(request):
    cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
    productions = []
    for cooperative in cooperatives :
        producs = Production.objects.filter(parcelle__producteur__cooperative_id=cooperative)
        for production in producs :
            if production.parcelle.producteur.cooperative_id == cooperative.id :
                productions.append(production)

    ctx = {
        'productions': productions
    }
    return render(request, 'clients/production.html', ctx)

def planting(request):
    cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
    plantings = []
    for cooperative in cooperatives :
        plants = Planting.objects.filter(parcelle__producteur__cooperative=cooperative)
        for plant in plants :
            if plant.parcelle.producteur.cooperative_id == cooperative.id :
                plantings.append(plant)
        #Planting.objects.all().order_by('-date')


    ctx = {
        'plantings': plantings
    }
    return render(request, 'clients/plantings.html', ctx)



def detail_planting(request, code=None):
    activate = "plantings"
    instance = get_object_or_404(Planting, code=code)
    Details_Planting = DetailPlanting.objects.filter(planting_id=instance)

    Monitorings = Monitoring.objects.filter(planting_id=instance)
    remplacements = RemplacementMonitoring.objects.filter(monitoring__planting_id = instance.code)

    for remp in remplacements :
        remp.mort = MonitoringEspeceremplacement.objects.filter(remplacement_id = remp.code).aggregate(total=Sum('mort'))['total']
        remp.remplacer = MonitoringEspeceremplacement.objects.filter(remplacement_id = remp.code).aggregate(total=Sum('remplacer'))['total']
        #print(remp.mort)

    for monitoring in Monitorings:
        try:
            monitoring.remplacer = RemplacementMonitoring.objects.filter(monitoring_id = monitoring.code).latest('code')

        except RemplacementMonitoring.DoesNotExist:
            pass





    try:
        lastMonitoring = Monitoring.objects.filter(planting_id=instance).latest('code')
        context = {
            'instance':instance,
            'Details_Planting':Details_Planting,
            'Monitorings':Monitorings,
            "activate": activate,
            "lastMonitoring":lastMonitoring,
            "remplacements":remplacements


         }


    except Monitoring.DoesNotExist:
             context = {
            'instance':instance,
            'Details_Planting':Details_Planting,
            'Monitorings':Monitorings,
            "activate": activate,
            "remplacements":remplacements


         }

    return render(request, 'clients/Coop/detail_planting.html', context)






def export_planting_xls(request, id=None):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="producteurs.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Producteurs')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODE', 'PRODUCTEUR', 'ESPECE', 'QTE']
    cooperative = get_object_or_404(Cooperative, id=id)

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative.id).values_list(
        'planting__parcelle__code',
        'planting__parcelle__producteur__nom',
        # 'planting__parcelle__producteur__section__libelle',
        'espece__libelle',
        'nb_plante',
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


#---------------------------------16/06/2022-----------------------------MPI--------------------------------

@api_view(['GET'])
def camp_filterdashboad(request):
    code = request.GET.get('code')
    production = 0
    petite_production = 0
    grande_production = 0
    nb_cooperatives = 0
    nb_parcelles = 0
    Superficie = 0
    nb_producteurs = 0
    Total_plant = 0

    if code == "":
        cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)

        for cooperative in cooperatives :

            if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total']) != None:
                production = production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('qteProduct'))['total'])

            if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total']) != None :
                petite_production = petite_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total'])

            if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total']) != None :
                grande_production = grande_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total'])


            nb_producteurs = nb_producteurs + Producteur.objects.filter(cooperative_id=cooperative.id).filter(created_at__contains = code).count()
            prod_coop = Cooperative.objects.filter(id = cooperative.id).annotate(nb_producteur=Count('producteurs'))
            nb_cooperatives = nb_cooperatives + Cooperative.objects.filter(id = cooperative.id).count()
            section_coop = Cooperative.objects.filter(id = cooperative.id).annotate(nb_section=Count('sections'))
            nb_parcelles = nb_parcelles + Parcelle.objects.filter(producteur__cooperative=cooperative).count()
            if Parcelle.objects.filter(producteur__cooperative=cooperative).aggregate(total=Sum('superficie'))['total'] != None :
                Superficie = Superficie + Parcelle.objects.filter(producteur__cooperative=cooperative).aggregate(total=Sum('superficie'))['total']

            if Planting.objects.filter(parcelle__producteur__cooperative=cooperative).aggregate(total=Sum('plant_recus'))['total'] != None :
                Total_plant = Total_plant + Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).aggregate(total=Sum('plant_recus'))['total']



        production = production /1000
        petite_production = petite_production /1000
        grande_production = grande_production /1000




        querysets =[]
        if len(cooperatives) >= 1 :

            for coop in cooperatives:
                coop.parcelles =  Parcelle.objects.filter(producteur__cooperative=coop).count()
                coop.prod =  Producteur.objects.filter(cooperative_id=coop.id).filter(created_at__contains = code).count()
                coop.productions = Production.objects.filter(parcelle__producteur__cooperative=coop).aggregate(total=Sum('qteProduct'))['total']
                coop.plants = Planting.objects.filter(parcelle__producteur__cooperative=coop).aggregate(total=Sum('plant_recus'))['total']
                if Parcelle.objects.filter(producteur__cooperative=coop).aggregate(total=Sum('superficie'))[ 'total'] != None :
                    coop.superficies = int(Parcelle.objects.filter(producteur__cooperative=coop).aggregate(total=Sum('superficie'))[ 'total'])
                query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=coop.id).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
                for q in query :
                    querysets.append(q)

        elif len(cooperatives) == 1 :
            cooperatives.parcelles = Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).count()
            coop.prod =  Producteur.objects.filter(cooperative_id=cooperatives.id).filter(created_at__contains = code).count()
            cooperatives.productions = Production.objects.filter(parcelle__producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('qteProduct'))['total']
            cooperatives.plants = Planting.objects.filter(parcelle__producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('plant_recus'))['total']
            if Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('superficie'))[ 'total'] != None:
                cooperatives.superficies = int(Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).aggregate(total=Sum('superficie'))[ 'total'])
            query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperatives.id).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
            for q in query :
                querysets.append(q)


        labels = []
        data = []
        for stat in querysets:
            labels.append(stat['espece__libelle'])
            data.append(stat['nb_plante'])


        context = {
                'cooperatives': cooperatives,
                # 'AllCooperatives': AllCooperatives,
                'nb_cooperatives': nb_cooperatives,
                'nb_producteurs': nb_producteurs,
                'nb_parcelles': nb_parcelles,
                'Superficie': Superficie,
                'Total_plant': Total_plant,
                'prod_coop': prod_coop,
                'section_coop': section_coop,
                'production': production,
                'petite_production': petite_production,
                'grande_production': grande_production,
                'annee':code,
                'labels':labels,
                'data':data
                # 'activate': activate
                # 'section_cooperative': section_cooperative,
            }


        templateStr = render_to_string('clients/campfilter.html',context)
        return JsonResponse({'templateStr': templateStr, 'code': code}, safe=False)
    else :
        cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
        prod_coop = 0
        section_coop = 0
        for cooperative in cooperatives :
            if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(created_at__contains = code).aggregate(total=Sum('qteProduct'))['total']) != None:
                production = production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(created_at__contains = code).aggregate(total=Sum('qteProduct'))['total'])

            if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="PETITE").filter(created_at__contains = code).aggregate(total=Sum('qteProduct'))['total']) != None :
                petite_production = petite_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(created_at__contains = code).filter(campagne="PETITE").aggregate(total=Sum('qteProduct'))['total'])

            if (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(campagne="GRANDE").filter(created_at__contains = code).aggregate(total=Sum('qteProduct'))['total']) != None :
                grande_production = grande_production + (Production.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(created_at__contains = code).filter(campagne="GRANDE").aggregate(total=Sum('qteProduct'))['total'])


            nb_producteurs = nb_producteurs + Producteur.objects.filter(cooperative_id=cooperative.id).filter(created_at__contains = code).count()
            prod_coop = Cooperative.objects.filter(id = cooperative.id).filter(created_at__contains = code).annotate(nb_producteur=Count('producteurs'))
            nb_cooperatives = nb_cooperatives + Cooperative.objects.filter(id = cooperative.id).filter(created_at__contains = code).count()
            section_coop = Cooperative.objects.filter(id = cooperative.id).filter(created_at__contains = code).annotate(nb_section=Count('sections'))
            nb_parcelles = nb_parcelles + Parcelle.objects.filter(producteur__cooperative=cooperative).filter(created_at__contains = code).count()
            if Parcelle.objects.filter(producteur__cooperative=cooperative).filter(created_at__contains = code).aggregate(total=Sum('superficie'))['total'] != None :
                Superficie = Superficie + Parcelle.objects.filter(producteur__cooperative=cooperative).filter(created_at__contains = code).aggregate(total=Sum('superficie'))['total']

            if Planting.objects.filter(parcelle__producteur__cooperative=cooperative).filter(created_at__contains = code).aggregate(total=Sum('plant_recus'))['total'] != None :
                Total_plant = Total_plant + Planting.objects.filter(parcelle__producteur__cooperative_id=cooperative).filter(created_at__contains = code).aggregate(total=Sum('plant_recus'))['total']


        production = production /1000
        petite_production = petite_production /1000
        grande_production = grande_production /1000





        querysets =[]
        if len(cooperatives) >= 1 :

            for coop in cooperatives:
                coop.parcelles =  Parcelle.objects.filter(producteur__cooperative=coop).filter(created_at__contains = code).count()
                coop.prod =  Producteur.objects.filter(cooperative_id=coop.id).filter(created_at__contains = code).count()
                coop.productions = Production.objects.filter(parcelle__producteur__cooperative=coop).filter(created_at__contains = code).aggregate(total=Sum('qteProduct'))['total']
                coop.plants = Planting.objects.filter(parcelle__producteur__cooperative=coop).filter(created_at__contains = code).aggregate(total=Sum('plant_recus'))['total']
                if Parcelle.objects.filter(producteur__cooperative=coop).filter(created_at__contains = code).aggregate(total=Sum('superficie'))[ 'total'] != None :
                    coop.superficies = int(Parcelle.objects.filter(producteur__cooperative=coop).filter(created_at__contains = code).aggregate(total=Sum('superficie'))[ 'total'])
                query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=coop.id).filter(created_at__contains = code).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
                for q in query :
                    querysets.append(q)

        elif len(cooperatives) == 1 :
            cooperatives.parcelles = Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).filter(created_at__contains = code).count()
            cooperatives.prod =  Producteur.objects.filter(cooperative_id=cooperatives.id).filter(created_at__contains = code).count()
            cooperatives.productions = Production.objects.filter(parcelle__producteur__cooperative__utilisateur=request.user.utilisateur).filter(created_at__contains = code).aggregate(total=Sum('qteProduct'))['total']
            cooperatives.plants = Planting.objects.filter(parcelle__producteur__cooperative__utilisateur=request.user.utilisateur).filter(created_at__contains = code).aggregate(total=Sum('plant_recus'))['total']
            if Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).filter(created_at__contains = code).aggregate(total=Sum('superficie'))[ 'total'] != None:
                cooperatives.superficies = int(Parcelle.objects.filter(producteur__cooperative__utilisateur=request.user.utilisateur).filter(created_at__contains = code).aggregate(total=Sum('superficie'))[ 'total'])
            query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperatives.id).filter(created_at__contains = code).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
            for q in query :
                querysets.append(q)


        labels = []
        data = []
        for stat in querysets:
            labels.append(stat['espece__libelle'])
            data.append(stat['nb_plante'])


        context = {
                'cooperatives': cooperatives,
                # 'AllCooperatives': AllCooperatives,
                'nb_cooperatives': nb_cooperatives,
                'nb_producteurs': nb_producteurs,
                'nb_parcelles': nb_parcelles,
                'Superficie': Superficie,
                'Total_plant': Total_plant,
                'prod_coop': prod_coop,
                'section_coop': section_coop,
                'production': production,
                'petite_production': petite_production,
                'grande_production': grande_production,
                'annee':code,
                'labels':labels,
                'data':data,
                # 'section_cooperative': section_cooperative,
            }


        templateStr = render_to_string('clients/campfilter.html',context)
        return JsonResponse({'templateStr': templateStr, 'code': code}, safe=False)



# def DetailPlantingsbyYear(request,code):
#     querysets = []
#     cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur).filter(created_at__contains = code)
#     for cooperative in cooperatives :
#         query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id=cooperative).filter(created_at__contains = code).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
#         for q in query :
#             querysets.append(q)


#     labels = []
#     data = []
#     for stat in querysets:
#         labels.append(stat['espece__libelle'])
#         data.append(stat['nb_plante'])

#     return JsonResponse(data={
#         'labels': labels,
#         'data': data,
#     })



def DetailPlantingsbyYear(request,code):
    querysets = []
    cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
    # for cooperative in cooperatives :
    query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id__in=cooperatives).filter(created_at__contains = code).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    for q in query :
        querysets.append(q)


    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


def DetailPlantingsbyNoyear(request):
    querysets = []
    cooperatives = Cooperative.objects.filter(utilisateur = request.user.utilisateur)
    query = DetailPlanting.objects.filter(planting__parcelle__producteur__cooperative_id__in=cooperatives).values("espece__libelle").annotate(nb_plante=Sum('nb_plante'))
    for q in query :
        querysets.append(q)


    labels = []
    data = []
    for stat in querysets:
        labels.append(stat['espece__libelle'])
        data.append(stat['nb_plante'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })
    
    
def noClusterCarte(request):
    cooperatives = Cooperative.objects.filter(utilisateur=request.user.utilisateur)
    cluster = 1
    context = {
        'cooperatives': cooperatives,
        "cluster":cluster
    }
    return render(request, 'carte.html', context)


    # prods= Producteur.objects.all()
    # producteurs = []
    # for product in prods :
    #     for cooperative in cooperatives :
    #         if product.cooperative_id == cooperative.id :
    #             producteurs.append(product)



    # for prod in producteurs:
    #      prod.superficies = Parcelle.objects.filter(producteur=prod).aggregate(total=Sum('superficie'))['total']


    # ctx = {
        # 'producteurs' : producteurs
    # }
    
#############datatable cote client ###################
@api_view(['POST'])
def prodClientTableFunction(request):
    draw = request.POST['draw']
    row = request.POST['start']
    rowperpage = request.POST['length']
    columIndex = request.POST['order[0][column]']
    columnName = request.POST['columns['+columIndex+'][data]']
    columnSortOrder = request.POST['order[0][dir]']
    searchValue = request.POST['search[value]']
    
    cooperatives = Cooperative.objects.filter(utilisateur=request.user.utilisateur)
    arrayProd = []
    
    prodLong = Producteur.objects.filter(cooperative_id__in = cooperatives)
    recherche = Producteur.objects.filter(cooperative_id__in = cooperatives).filter(Q(code__contains = searchValue) 
                                               | Q(cooperative__sigle__contains = searchValue) 
                                               | Q(section__libelle__contains = searchValue)
                                               | Q(nom__contains = searchValue)
                                               | Q(localite__contains = searchValue)
                                               | Q(contacts__contains = searchValue)
                                               )
    
    if searchValue == "":
        producteurs= Producteur.objects.filter(cooperative_id__in = cooperatives).order_by("-created_at")[int(row):int(row)+int(rowperpage)]
        for prod in producteurs :
            superficies = Parcelle.objects.filter(producteur=prod).aggregate(total=Sum('superficie'))['total']
            
            if superficies:
                superficies = "{:.2f}".format(superficies)
            else:
                superficies = "{:.2f}".format(0)
                
                
            item = {
               "code": prod.code,
               "cooperative": prod.cooperative.sigle,
               "section": prod.section.libelle,
               "nom": prod.nom,
               "localite":prod.localite,
               "contact": prod.contacts,
               "nbre_parcelle": prod.nb_parcelle,
               "superficie": superficies
            }
            
            arrayProd.append(item)
            
    else:
        producteurs= Producteur.objects.filter(cooperative_id__in = cooperatives).filter(Q(code__contains = searchValue) 
                                               | Q(cooperative__sigle__contains = searchValue) 
                                               | Q(section__libelle__contains = searchValue)
                                               | Q(nom__contains = searchValue)
                                               | Q(localite__contains = searchValue)
                                               | Q(contacts__contains = searchValue)
                                               ).order_by("-created_at")[int(row):int(row)+int(rowperpage)]
        for prod in producteurs :
            superficies = Parcelle.objects.filter(producteur=prod).aggregate(total=Sum('superficie'))['total']
            
            if superficies:
                superficies = "{:.2f}".format(superficies)
            else:
                superficies = "{:.2f}".format(0)
                
                
            item = {
               "code": prod.code,
               "cooperative": prod.cooperative.sigle,
               "section": prod.section.libelle,
               "nom": prod.nom,
               "localite":prod.localite,
               "contact": prod.contacts,
               "nbre_parcelle": prod.nb_parcelle,
               "superficie": superficies
            }
            
            arrayProd.append(item)
            
            
            
    return JsonResponse({
        'draw':int(draw),
        'recordsTotal' : len(prodLong),
        'recordsFiltered':len(recherche),
        'aaData': arrayProd,
        },safe=True)
    

@api_view(['POST'])
def parcClientTableFunction(request):
    draw = request.POST['draw']
    row = request.POST['start']
    rowperpage = request.POST['length']
    columIndex = request.POST['order[0][column]']
    columnName = request.POST['columns['+columIndex+'][data]']
    columnSortOrder = request.POST['order[0][dir]']
    searchValue = request.POST['search[value]']
    
    cooperative = Cooperative.objects.filter(utilisateur=request.user.utilisateur)
    arrayParc = []
    
    parcLong = Parcelle.objects.filter(producteur__cooperative_id__in=cooperative)
    recherche = Parcelle.objects.filter(producteur__cooperative_id__in=cooperative).filter(Q(code__contains = searchValue)
                                            | Q(type_parcelle__contains=searchValue)
                                            | Q(producteur__nom__contains = searchValue)
                                            | Q(producteur__cooperative__sigle__contains = searchValue)
                                            | Q(producteur__section__libelle__contains = searchValue)
                                            | Q(code__contains = searchValue)
                                            | Q(code_certificat__contains = searchValue)
                                            | Q(producteur__localite__contains = searchValue)
                                            | Q(longitude__contains= searchValue)
                                            | Q(latitude__contains = searchValue)
                                            | Q(superficie__contains = searchValue)
                                            )
    
    if searchValue == "":
        parcelles = Parcelle.objects.filter(producteur__cooperative_id__in=cooperative).order_by("-created_at")[int(row):int(row)+int(rowperpage)]
        for parc in parcelles :
            recus = Planting.objects.filter(parcelle=parc).aggregate(total=Sum('plant_recus'))['total']
            plante = DetailPlanting.objects.filter(planting__parcelle=parc).aggregate(total=Sum('nb_plante'))['total']
            
            item = {
                "type" : parc.type_parcelle,
                "cooperative": parc.producteur.cooperative.sigle,
                "section": parc.producteur.section.libelle,
                "producteur": parc.producteur.nom,
                "code": parc.code,
                "code_certificat": parc.code_certificat,
                "localite": parc.producteur.localite,
                "coordonnee": '<span class="text-center"> "{0}","{1}" </span>'.format(parc.longitude,parc.latitude),
                "superficie": parc.superficie,
                "recus":recus,
                "plante": plante
            }
            
            arrayParc.append(item)
    else:
        parcelles = Parcelle.objects.filter(producteur__cooperative_id__in=cooperative).filter(Q(code__contains = searchValue)
                                            | Q(type_parcelle__contains=searchValue)
                                            | Q(producteur__cooperative__sigle__contains = searchValue)
                                            | Q(producteur__section__libelle__contains = searchValue)
                                            | Q(producteur__nom__contains = searchValue)
                                            | Q(code__contains = searchValue)
                                            | Q(code_certificat__contains = searchValue)
                                            | Q(producteur__localite__contains = searchValue)
                                            | Q(longitude__contains= searchValue)
                                            | Q(latitude__contains = searchValue)
                                            | Q(superficie__contains = searchValue)
                                            ).order_by("-created_at")[int(row):int(row)+int(rowperpage)]
        
        for parc in parcelles :
            recus = Planting.objects.filter(parcelle=parc).aggregate(total=Sum('plant_recus'))['total']
            plante = DetailPlanting.objects.filter(planting__parcelle=parc).aggregate(total=Sum('nb_plante'))['total']
            
            item = {
                "type" : parc.type_parcelle,
                "cooperative": parc.producteur.cooperative.sigle,
                "section": parc.producteur.section.libelle,
                "producteur": parc.producteur.nom,
                "code": parc.code,
                "code_certificat": parc.code_certificat,
                "localite": parc.producteur.localite,
                "coordonnee": '<span class="text-center"> "{0}","{1}" </span>'.format(parc.longitude,parc.latitude),
                "superficie": parc.superficie,
                "recus":recus,
                "plante": plante
            }
            
            arrayParc.append(item)
            
            
    return JsonResponse({
        'draw':int(draw),
        'recordsTotal' : len(parcLong),
        'recordsFiltered':len(recherche),
        'aaData': arrayParc,
        },safe=False)
        
    


@api_view(['POST'])
def coopClientTableFunction(request):
    draw = request.POST['draw']
    row = request.POST['start']
    rowperpage = request.POST['length']
    columIndex = request.POST['order[0][column]']
    columnName = request.POST['columns['+columIndex+'][data]']
    columnSortOrder = request.POST['order[0][dir]']
    searchValue = request.POST['search[value]']
    
    coopLong = Cooperative.objects.filter(utilisateur=request.user.utilisateur)
    recherche = Cooperative.objects.filter(utilisateur=request.user.utilisateur).filter(Q(region__libelle__contains = searchValue)
                                                  | Q(sigle__contains = searchValue)
                                                  | Q(siege__contains = searchValue)
                                                  | Q(contacts__contains = searchValue)
                                                  
                                                  )
    
    arrayCoop = []
    
    if searchValue == "" :
        cooperatives = Cooperative.objects.filter(utilisateur=request.user.utilisateur).order_by("sigle")[int(row):int(row)+int(rowperpage)]
        for coop in cooperatives :
            nbreSection = Section.objects.filter(cooperative_id = coop.id).count()
            nbreProd = Producteur.objects.filter(cooperative_id = coop.id).count()
            nbreParc = Parcelle.objects.filter(producteur__cooperative_id = coop.id).count()
            nbreSuperficie = Parcelle.objects.filter(producteur__cooperative_id=coop.id).aggregate(total=Sum('superficie'))[ 'total']
            
            if nbreSuperficie:
                nbreSuperficie = "{:.2f}".format(nbreSuperficie)
            else:
                nbreSuperficie = "{:.2f}".format(0)
            
            item = {
                "region": coop.region.libelle,
                "sigle": coop.sigle,
                "siege": coop.siege,
                "contact" : coop.contacts,
                "nbre_section": nbreSection,
                "nbre_producteur":nbreProd,
                "nbre_parcelle":nbreParc,
                "superficie":nbreSuperficie,
                "action": '<a href="{0}" class="btn btn-primary btn-xs">Accéder</a>'.format(
                    reverse('clients:detail_coop', args=[coop.id])
                )
                
            }
            
            arrayCoop.append(item)
    else:
        cooperatives = Cooperative.objects.filter(utilisateur=request.user.utilisateur).filter(Q(region__libelle__contains = searchValue)
                                                  | Q(sigle__contains = searchValue)
                                                  | Q(siege__contains = searchValue)
                                                  | Q(contacts__contains = searchValue)
                                                  ).order_by("-sigle")[int(row):int(row)+int(rowperpage)]
        
        
        for coop in cooperatives :
            nbreSection = Section.objects.filter(cooperative_id = coop.id).count()
            nbreProd = Producteur.objects.filter(cooperative_id = coop.id).count()
            nbreParc = Parcelle.objects.filter(producteur__cooperative_id = coop.id).count()
            nbreSuperficie = Parcelle.objects.filter(producteur__cooperative_id=coop.id).aggregate(total=Sum('superficie'))[ 'total']
            
            if nbreSuperficie:
                nbreSuperficie = "{:.2f}".format(nbreSuperficie)
            else:
                nbreSuperficie = "{:.2f}".format(0)
            
            item = {
                "region": coop.region.libelle,
                "sigle": coop.sigle,
                "siege": coop.siege,
                "contact" : coop.contacts,
                "nbre_section": nbreSection,
                "nbre_producteur":nbreProd,
                "nbre_parcelle":nbreParc,
                "superficie":nbreSuperficie,
                "action": '<a href="{0}" class="btn btn-primary btn-xs">Accéder</a>'.format(
                    reverse('clients:detail_coop', args=[coop.id])
                )
                
            }
            
            arrayCoop.append(item)
        
    return JsonResponse({
        'draw':int(draw),
        'recordsTotal' : len(coopLong),
        'recordsFiltered':len(recherche),
        'aaData': arrayCoop,
        },safe=False)
    
    
    
    