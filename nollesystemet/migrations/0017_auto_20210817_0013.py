# Generated by Django 3.2.5 on 2021-08-16 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nollesystemet', '0016_auto_20210816_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='campussafaristation',
            name='responsible',
            field=models.ManyToManyField(limit_choices_to={'user_type__in': [1, 6, 5]}, related_name='campus_safari_stations', to='nollesystemet.UserProfile'),
        ),
        migrations.AlterField(
            model_name='campussafarigroup',
            name='responsible_fadders',
            field=models.ManyToManyField(limit_choices_to={'user_type__in': [1, 6, 5]}, related_name='campus_safari_groups', to='nollesystemet.UserProfile'),
        ),
    ]