# Generated by Django 5.0.1 on 2024-09-19 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crt_app', '0008_remove_college_branch_remove_user_specialisation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='year',
            field=models.IntegerField(),
        ),
    ]
