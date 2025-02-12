# Generated by Django 4.1.6 on 2023-03-02 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0008_remove_basescript_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseCommand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('parameters', models.TextField()),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scripts.basescript')),
            ],
        ),
    ]
