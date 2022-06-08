from django.contrib.auth.models import User
from rest_framework import serializers

from cooperatives.models import DetailMonitoring, DetailPlantingRemplacement, Monitoring, MonitoringEspece, Producteur, Parcelle, RemplacementMonitoring, Section, Sous_Section, Cooperative, Formation, Planting, DetailPlanting
from parametres.models import Pepiniere, Projet, Projet_Cat, Campagne, Espece, Cat_Plant, Origine, Sous_Prefecture, Utilisateur
from clients.models import Client


class UtilisateurUserSerialiser(serializers.ModelSerializer):
    
    class Meta:
        model = Utilisateur
        fields = ('contact','cooperative','role')

class UserSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurUserSerialiser(source = 'utilisateur')

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'last_name',
            'first_name',
            'utilisateur'
        )



class OrigineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origine
        fields = (
            'id',
            'code',
            'pays'
        )

class SousPrefectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sous_Prefecture
        fields = (
            'id',
            'libelle',
        )

class CampagneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campagne
        fields = (
            'id',
            'titre',
            'mois_debut',
            'annee_debut',
            'mois_fin',
            'annee_fin'
        )

class CategorieEspeceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat_Plant
        fields = (
            'id',
            'libelle',
    )

class EspeceSerializer(serializers.ModelSerializer):
    categorie = CategorieEspeceSerializer(read_only=True)
    class Meta:
        model = Espece
        fields = (
            'id',
            'categorie',
            'accronyme',
            'libelle',
        )
    #     depth = 1
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['categorie'] = CategorieEspeceSerializer(instance.categorie).data
    #     return response

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Client
        fields = (
            'id',
            'user',
            'sigle',
            'contacts',
            'libelle',
            'pays',
            'adresse',
            'telephone1',
            'telephone2',
            'email',
            'siteweb',
            'logo',
        )

class CategorieProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet_Cat
        fields = (
            'id',
            "libelle"
        )

class ProjetSerializer(serializers.ModelSerializer):
    # categorie = CategorieProjetSerializer(read_only=True)
    class Meta:
        model = Projet
        fields = (
            'id',
            "categorie",
            "titre",
            "chef",
            "debut",
            "fin",
            "etat",
        )
        depth = 1
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['categorie'] = CategorieProjetSerializer(instance.categorie).data
        return response

class CooperativeSerializer(serializers.ModelSerializer):
    # projet = ProjetSerializer(many=True)
    class Meta:
        model=Cooperative
        fields = (
            'id',
            'user',
            'region',
            'sigle',
            'projet',
            'contacts',
            'logo',
            'appartenance'
        )
        depth = 1
    def to_representation(self, instance):
        response = super().to_representation(instance)
        # response['region'] = ClientSerializer(instance.client).data
        # response['projet'] = ProjetSerializer(instance.projet).data
        return response

class SectionSerializer(serializers.ModelSerializer):
    # cooperative = CooperativeSerializer(read_only=True)
    class Meta:
        model = Section
        fields = (
            'id',
            "cooperative",
            'libelle',
            'responsable',
            'contacts',
        )
        depth = 1
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['cooperative'] = CooperativeSerializer(instance.cooperative).data
    #     # response['sous_section'] = SousSectionSerializer(instance.sous_section).data
    #     return response

class SousSectionSerializer(serializers.ModelSerializer):
    section = SectionSerializer(read_only=True)
    class Meta:
        model = Sous_Section
        fields = (
            'id',
            'libelle',
            'responsable',
            'contacts',
            'section',
        )
    #     depth = 1
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['section'] = SectionSerializer(instance.section).data
    #     # response['sous_section'] = SousSectionSerializer(instance.sous_section).data
    #     return response

class ProducteurSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Producteur
        fields = (
            'code',
            'origine',
            'cooperative',
            'sous_prefecture',
            'type_producteur',
            'nom',
            'dob',
            'genre',
            'contacts',
            'localite',
            'section',
            'sous_section',
            'nb_parcelle',
            'image',
            'type_document',
            'num_document',
            'document',
            'nb_enfant',
            'nb_epouse',
            'enfant_scolarise',
            'nb_personne',
            'user_id',
            'created_at',
            'updated_at'
        )
        depth = 1
    

class ParcelleSerializer(serializers.ModelSerializer):
    #producteur = ProducteurSerializer(many=True)
    class Meta:
        model=Parcelle
        fields = (
            'code',
            'producteur',
            'acquisition',
            'latitude',
            'longitude',
            'culture',
            'certification',
            'superficie',
            'projet',
            'code_certificat',
            'annee_certificat',
            'annee_acquis',
            'user_id',
            'created_at',
            'updated_at'
        )
        depth = 1

    #def to_representation(self, instance):
    #    response = super().to_representation(instance)
    #    response['producteur'] = ProducteurSerializer(instance.producteur).data
     #   return response

class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = [
            'cooperative',
            'projet',
            'formateur',
            'libelle',
            'details',
            'observation',
            'debut',
            'fin',
        ]
        depth = 1
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['cooperative'] = CooperativeSerializer(instance.cooperative).data
        response['projet'] = ProjetSerializer(instance.projet).data
        return response

class PlantingSerializer(serializers.ModelSerializer):
    campagne = CampagneSerializer(read_only=True)
    parcelle = ParcelleSerializer(read_only=True)
    class Meta:
        model = Planting
        fields = (
            'code',
            "campagne",
            "parcelle",
            "nb_plant_exitant",
            "plant_recus",
            "plant_total",
            "date",
            'user_id'
        )
        depth = 1
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['parcelle'] = ParcelleSerializer(instance.parcelle).data
        # response['projet'] = ProjetSerializer(instance.projet).data
        # response['campagne'] = CampagneSerializer(instance.campagne).data
        return response

class DetailsPlantingSerializer(serializers.ModelSerializer):
    planting = PlantingSerializer(read_only=True)
    espece = EspeceSerializer(read_only=True)
    class Meta:
        model = DetailPlanting
        fields = (
            'code',
            "planting",
            "espece",
            "nb_plante",
        )
        depth = 1

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # response['planting'] = PlantingSerializer(instance.planting).data
        # response['espece'] = EspeceSerializer(instance.espece).data
        # response['campagne'] = CampagneSerializer(instance.campagne).data
        return response



class PepiniereSerializer(serializers.ModelSerializer):
    #producteur = ProducteurSerializer(many=True)
    class Meta:
        model=Pepiniere
        fields=( 
            'id',
            'projet',
            'campagne',
            'region',
            'ville',
            'site',
            'latitude',
            'longitude',
            'technicien',
            'contacts_technicien',
            'superviseur',
            'contacts_superviseur',
            #'fournisseur',
            #'contacts_fournisseur',
            'sachet_recus',
            'production_plant',
            'production_realise',
            'plant_mature',
            'plant_retire',
        )
        depth = 1

    #def to_representation(self, instance):
    #    response = super().to_representation(instance)
    #    response['producteur'] = ProducteurSerializer(instance.producteur).data
     #   return response



class MonitoringSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Monitoring
        fields=( 
            'code',
            'planting',
            'mort_global',
            'mature_global',
            'date',

        )
        # depth = 1


class RemplacementMonitoringSerializer(serializers.ModelSerializer):

    class Meta:
        model=RemplacementMonitoring
        fields=( 
            'code',
            'date',
            'espece',
            'monitoring',
        )
        depth = 1


class DetailPlantingRemplacementSerializer(serializers.ModelSerializer):

    class Meta:
        model=DetailPlantingRemplacement
        fields=( 
            'code',
            'planting',
            'espece',
            'nb_plante',
            'remplacer',
        )
        depth = 1


class MonitoringEspeceSerializer(serializers.ModelSerializer):

    class Meta:
        model=MonitoringEspece
        fields=( 
            'code',
            'detailmonitoring',
            'espece',
            'detailplanting',
            'mort',
            'detailplantingremplacement',
            'taux_mortalite',
        )
        depth = 1


class DetailMonitoringSerializer(serializers.ModelSerializer):

    class Meta:
        model=DetailMonitoring
        fields=( 
            'code',
            'monitoring',
            'espece',
        )
        depth = 1


