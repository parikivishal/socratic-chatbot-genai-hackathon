# Generated by Django 5.0.6 on 2024-09-29 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chatbot', '0002_rename_register_userregistration'),
    ]

    operations = [
        migrations.AddField(
            model_name='userregistration',
            name='username',
            field=models.CharField(default='blume', max_length=200),
        ),
        migrations.AlterField(
            model_name='userregistration',
            name='email',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
