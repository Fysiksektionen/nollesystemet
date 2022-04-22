# Generated by Django 3.2.5 on 2021-08-15 15:26

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nollesystemet', '0014_alter_happening_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='happening',
            name='automatic_confirmation',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[(1, 'Fadder'), (2, 'nØllan'), (3, 'Senior'), (4, 'Extern'), (5, 'Administrativ'), (6, 'Förfadder')], max_length=11),
        ),
        migrations.AlterField(
            model_name='happening',
            name='user_types',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[(1, 'Fadder'), (2, 'nØllan'), (3, 'Senior'), (4, 'Extern'), (5, 'Administrativ'), (6, 'Förfadder')], max_length=11),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Fadder'), (2, 'nØllan'), (3, 'Senior'), (4, 'Extern'), (5, 'Administrativ'), (6, 'Förfadder')], verbose_name='Användartyp'),
        ),
        migrations.AlterField(
            model_name='usertypebaseprice',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Fadder'), (2, 'nØllan'), (3, 'Senior'), (4, 'Extern'), (5, 'Administrativ'), (6, 'Förfadder')]),
        ),
    ]