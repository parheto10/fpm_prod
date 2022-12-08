# Generated by Django 3.2.13 on 2022-06-29 15:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0007_alter_utilisateur_contact'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cooperatives', '0009_alter_parcelle_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncHistorique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('status', models.IntegerField(blank=True, default=0, null=True)),
                ('indice', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cooperative', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.cooperative')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]