# Generated by Django 3.2.13 on 2022-06-24 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0006_auto_20220624_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilisateur',
            name='contact',
            field=models.CharField(max_length=255),
        ),
    ]