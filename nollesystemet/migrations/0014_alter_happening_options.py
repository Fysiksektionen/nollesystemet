# Generated by Django 3.2.5 on 2021-08-14 01:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nollesystemet', '0013_registration_ocr'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='happening',
            options={'permissions': [('create_happening', 'Can create happenings'), ('edit_happening', 'Can edit any happening'), ('control_payments', 'Can handle system wide payment information')], 'verbose_name': 'Evenemang', 'verbose_name_plural': 'Evenemang'},
        ),
    ]