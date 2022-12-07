# Generated by Django 3.2.13 on 2022-08-05 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cooperatives', '0010_synchistorique'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcelle',
            name='type_parcelle',
            field=models.CharField(choices=[('AGROFORESTERIE', 'AGROFORESTERIE'), ('COMMUNAUTAIRE', 'COMMUNAUTAIRE'), ('FORET_CLASSEE', 'FORET CLASSEE'), ('INDIVIDUELLE', 'INDIVIDUELLE')], default='AGROFORESTERIE', max_length=50),
        ),
    ]
