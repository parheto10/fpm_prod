# Generated by Django 3.2.13 on 2022-10-28 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0008_alter_campagne_options'),
        ('cooperatives', '0017_alter_parcelle_type_parcelle'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailmonitoring',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AddField(
            model_name='detailmonitoring',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='detailplanting',
            name='etat',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='detailplanting',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AddField(
            model_name='detailplanting',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='detailplantingremplacement',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AddField(
            model_name='detailplantingremplacement',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='monitoring',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AddField(
            model_name='monitoringespece',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AddField(
            model_name='monitoringespece',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='monitoringespeceremplacement',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AddField(
            model_name='monitoringespeceremplacement',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='planting',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AddField(
            model_name='remplacementmonitoring',
            name='synchro',
            field=models.CharField(default='OUI', max_length=10),
        ),
        migrations.AlterField(
            model_name='parcelle',
            name='code',
            field=models.CharField(help_text='LE CODE PARCELLE EST GENERE AUTOMATIQUEMENT', max_length=150, primary_key=True, serialize=False, unique=True, verbose_name='CODE PARCELLE'),
        ),
        migrations.AlterField(
            model_name='parcelle',
            name='superficie',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='parcelle',
            name='type_parcelle',
            field=models.CharField(choices=[('AGROFORESTERIE', 'AGROFORESTERIE'), ('COMMUNAUTAIRE', 'COMMUNAUTAIRE'), ('FORET_CLASSEE', 'FORET CLASSEE'), ('INDIVIDUELLE', 'INDIVIDUELLE'), ('JACHERE', 'JACHERE'), ('PRIVEE', 'PRIVEE')], default='AGROFORESTERIE', max_length=50),
        ),
        migrations.CreateModel(
            name='MonitoringObsMobile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('synchro', models.CharField(default='OUI', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('monitoring', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cooperatives.monitoring')),
                ('observation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parametres.obsmonitoring')),
            ],
        ),
    ]
