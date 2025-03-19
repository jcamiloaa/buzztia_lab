# Generated by Django 5.0.12 on 2025-03-18 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0002_alter_whatsappwebhookdata_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='whatsappwebhookdata',
            name='direction',
            field=models.CharField(choices=[('inbound', 'Mensaje Entrante'), ('outbound', 'Mensaje Saliente')], default='inbound', help_text='Dirección del mensaje (entrante/saliente)', max_length=10),
        ),
    ]
