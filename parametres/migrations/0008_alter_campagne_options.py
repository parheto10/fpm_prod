# Generated by Django 3.2.13 on 2022-08-16 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0007_alter_utilisateur_contact'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campagne',
            options={'ordering': ['titre'], 'verbose_name': 'campagne', 'verbose_name_plural': 'CAMPAGNES'},
        ),
    ]
