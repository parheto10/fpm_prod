# Generated by Django 4.1.3 on 2023-02-21 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0008_alter_campagne_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='espece',
            name='densite',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='DENSITE SPECIFIQUE'),
        ),
        migrations.AlterField(
            model_name='campagne',
            name='annee_debut',
            field=models.IntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023)], default=2023, verbose_name='Année début'),
        ),
        migrations.AlterField(
            model_name='campagne',
            name='annee_fin',
            field=models.IntegerField(default=2024, verbose_name='Année fin'),
        ),
        migrations.AlterField(
            model_name='cooperative',
            name='created_at',
            field=models.CharField(default=2023, max_length=150),
        ),
    ]
