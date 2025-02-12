# Generated by Django 4.1.6 on 2023-03-17 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0015_basescript_type_alter_basescript_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basecommand',
            name='parameters',
        ),
        migrations.CreateModel(
            name='Parameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('command', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scripts.basecommand')),
            ],
        ),
    ]
