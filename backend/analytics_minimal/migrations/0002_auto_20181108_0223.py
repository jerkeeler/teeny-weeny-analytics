# Generated by Django 2.1.2 on 2018-11-08 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_minimal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='referrer',
            field=models.TextField(blank=True, null=True),
        ),
    ]
