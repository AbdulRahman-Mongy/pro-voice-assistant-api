# Generated by Django 4.1.6 on 2023-02-07 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0002_basescript_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='basescript',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
