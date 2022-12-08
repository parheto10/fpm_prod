# Generated by Django 3.1.7 on 2022-05-03 22:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import parametres.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=500, verbose_name='NATURE ACTIVITE')),
            ],
            options={
                'verbose_name': 'activite',
                'verbose_name_plural': 'ACTIVITES',
                'ordering': ['libelle'],
            },
        ),
        migrations.CreateModel(
            name='Campagne',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(blank=True, editable=False, max_length=500, null=True)),
                ('mois_debut', models.CharField(choices=[('JAN', 'JANVIER'), ('FEV', 'FEVRIER'), ('MAR', 'MARS'), ('AVR', 'AVRIL'), ('MAI', 'MAI'), ('JUN', 'JUIN'), ('JUL', 'JUILLET'), ('AUG', 'AOUT'), ('SEP', 'SEPTEMBRE'), ('OCT', 'OCTOBRE'), ('NOV', 'NOVEMBRE'), ('DEC', 'DECEMBRE')], default='NOV', max_length=50)),
                ('annee_debut', models.IntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022)], default=2022, verbose_name='Année début')),
                ('mois_fin', models.CharField(choices=[('JAN', 'JANVIER'), ('FEV', 'FEVRIER'), ('MAR', 'MARS'), ('AVR', 'AVRIL'), ('MAI', 'MAI'), ('JUN', 'JUIN'), ('JUL', 'JUILLET'), ('AUG', 'AOUT'), ('SEP', 'SEPTEMBRE'), ('OCT', 'OCTOBRE'), ('NOV', 'NOVEMBRE'), ('DEC', 'DECEMBRE')], default='SEP', max_length=50)),
                ('annee_fin', models.IntegerField(default=2023, verbose_name='Année fin')),
            ],
            options={
                'verbose_name': 'campagne',
                'verbose_name_plural': 'CAMPAGNES',
                'ordering': ['-titre'],
            },
        ),
        migrations.CreateModel(
            name='Cat_Plant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=50, verbose_name='Categorie')),
            ],
            options={
                'verbose_name': 'categorie plant',
                'verbose_name_plural': 'CATEGORIES PLANTS',
                'ordering': ['libelle'],
            },
        ),
        migrations.CreateModel(
            name='DetailsSemenceEspece',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Espece',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accronyme', models.CharField(max_length=250, verbose_name='NOM SCIENTIFIQUE')),
                ('libelle', models.CharField(max_length=250, verbose_name='NOM USUEL')),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.cat_plant')),
            ],
            options={
                'verbose_name': 'espece',
                'verbose_name_plural': 'ESPECES',
                'ordering': ['libelle'],
            },
        ),
        migrations.CreateModel(
            name='Fournisseur',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pseudo', models.CharField(max_length=255)),
                ('ville', models.CharField(max_length=255)),
                ('localite', models.CharField(max_length=255)),
                ('contact', models.CharField(max_length=255, verbose_name='CONTACT')),
            ],
            options={
                'verbose_name': 'fournisseur',
                'verbose_name_plural': 'FOURNISSEURS',
            },
        ),
        migrations.CreateModel(
            name='ObsMonitoring',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Origine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2, verbose_name='CODE PAYS')),
                ('pays', models.CharField(max_length=255, verbose_name='PAYS')),
            ],
            options={
                'verbose_name': 'origine',
                'verbose_name_plural': 'ORIGINES',
                'ordering': ['pays'],
            },
        ),
        migrations.CreateModel(
            name='Pepiniere',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=250, verbose_name='DELEGATION REGIONALE')),
                ('ville', models.CharField(max_length=250, verbose_name='VILLE')),
                ('site', models.CharField(max_length=250, verbose_name='SITE')),
                ('latitude', models.CharField(blank=True, max_length=10, null=True)),
                ('longitude', models.CharField(blank=True, max_length=10, null=True)),
                ('technicien', models.CharField(max_length=255, verbose_name='NOM ET PRENOMS TECHNICIEN')),
                ('contacts_technicien', models.CharField(blank=True, max_length=50, null=True, verbose_name='CONTACTS TECHNICIEN')),
                ('superviseur', models.CharField(max_length=255, verbose_name='NOM ET PRENOMS TECHNICIEN')),
                ('contacts_superviseur', models.CharField(blank=True, max_length=50, null=True, verbose_name='CONTACTS SUPERVISUER')),
                ('sachet_recus', models.PositiveIntegerField(default=0, verbose_name='QTE TOTAL SACHET RECU')),
                ('production_plant', models.PositiveIntegerField(default=0, verbose_name='PLANTS A PRODUIRE')),
                ('production_realise', models.PositiveIntegerField(default=0, verbose_name='REALISATION')),
                ('pourcentage_prod', models.PositiveIntegerField(default=0, verbose_name='POURCENTAGE DE PRODUCTION')),
                ('plant_mature', models.PositiveIntegerField(default=0, verbose_name='NBRE PLANT MATURE')),
                ('plant_retire', models.PositiveIntegerField(default=0, verbose_name='NBRE TOTAL PLANT RETIRE')),
                ('add_le', models.DateTimeField(auto_now_add=True)),
                ('update_le', models.DateTimeField(auto_now=True)),
                ('campagne', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='parametres.campagne')),
            ],
            options={
                'verbose_name': 'pépinière',
                'verbose_name_plural': 'PEPINIERES',
            },
        ),
        migrations.CreateModel(
            name='Projet_Cat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=500, verbose_name='CATEGORIE PROJET')),
            ],
            options={
                'verbose_name': 'catégorie projet',
                'verbose_name_plural': 'CATEGORIES PROJETS',
                'ordering': ['libelle'],
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=250)),
            ],
            options={
                'verbose_name': 'region',
                'verbose_name_plural': 'REGIONS',
                'ordering': ['libelle'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=255, verbose_name='ROLE USER')),
            ],
        ),
        migrations.CreateModel(
            name='Sous_Prefecture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=250)),
            ],
            options={
                'verbose_name': 'sous prefecture',
                'verbose_name_plural': 'SOUS PREFECTURES',
                'ordering': ['libelle'],
            },
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.IntegerField()),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='parametres.role')),
            ],
        ),
        migrations.CreateModel(
            name='Semence_Pepiniere',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production', models.PositiveIntegerField(default=0, verbose_name='NB PLANTS A PRODUIRE')),
                ('qte_recu', models.PositiveIntegerField(default=0, verbose_name='QTE RECU')),
                ('date', models.DateField(verbose_name='DATE RECEPTION')),
                ('details', models.TextField(blank=True, null=True)),
                ('add_le', models.DateTimeField(auto_now_add=True)),
                ('update_le', models.DateTimeField(auto_now=True)),
                ('espece_recu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.espece')),
                ('fournisseur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='parametres.fournisseur')),
                ('pepiniere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.pepiniere')),
            ],
            options={
                'verbose_name': 'détail semence reçu',
                'verbose_name_plural': 'DETAILS SEMENCES RECUS',
            },
        ),
        migrations.CreateModel(
            name='Projet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sigle', models.CharField(max_length=255)),
                ('titre', models.CharField(max_length=500)),
                ('chef', models.CharField(max_length=255)),
                ('debut', models.DateField()),
                ('fin', models.DateField()),
                ('etat', models.CharField(choices=[('en_cours', 'EN COURS'), ('suspendu', 'SUSPENDU'), ('traite', 'TRAITE')], max_length=50)),
                ('categorie', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='parametres.projet_cat', verbose_name='CATEGORIE PROJET')),
            ],
            options={
                'verbose_name': 'projet',
                'verbose_name_plural': 'PROJETS',
                'ordering': ['sigle'],
            },
        ),
        migrations.CreateModel(
            name='Prime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=250)),
                ('prix', models.PositiveIntegerField(default=100, verbose_name='Prix/Kg')),
                ('campagne', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.campagne')),
            ],
            options={
                'verbose_name': 'prime',
                'verbose_name_plural': 'PRIMES',
            },
        ),
        migrations.AddField(
            model_name='pepiniere',
            name='projet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='parametres.projet'),
        ),
        migrations.CreateModel(
            name='Intitule_Formation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=255)),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.projet')),
            ],
            options={
                'verbose_name': 'theme formation',
                'verbose_name_plural': 'THEMES DES FORMATIONS',
            },
        ),
        migrations.CreateModel(
            name='Cooperative',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('siege', models.CharField(blank=True, max_length=255, null=True, verbose_name='SIEGE/LOCALITE')),
                ('sigle', models.CharField(max_length=500)),
                ('contacts', models.CharField(max_length=50)),
                ('appartenance', models.CharField(choices=[('COMMUNAUTE', 'COMMUNAUTE'), ('COOPERATIVE', 'COOPERATIVE')], default='', max_length=50)),
                ('logo', models.ImageField(blank=True, upload_to=parametres.models.upload_logo_site, verbose_name='logo')),
                ('projet', models.ManyToManyField(to='parametres.Projet')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cooperatives', to='parametres.region')),
                ('utilisateur', models.ManyToManyField(to='parametres.Utilisateur')),
            ],
            options={
                'verbose_name': 'cooperative',
                'verbose_name_plural': 'COOPERATIVES',
                'ordering': ['sigle'],
            },
        ),
    ]