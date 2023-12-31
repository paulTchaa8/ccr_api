# Generated by Django 3.2.5 on 2023-08-01 20:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_recepteur', models.CharField(max_length=255)),
                ('num_emetteur', models.CharField(max_length=255)),
                ('installation', models.CharField(max_length=255)),
                ('message', models.TextField(blank=True, null=True)),
                ('date_message', models.DateTimeField(auto_now_add=True)),
                ('emetteur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.emetteur')),
                ('recepteur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
