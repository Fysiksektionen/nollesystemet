# Generated by Django 3.2.5 on 2021-07-10 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_remove_authuser_auth_backend'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]