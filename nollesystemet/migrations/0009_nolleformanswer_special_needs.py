# Generated by Django 3.2.5 on 2021-07-29 08:07

from django.db import migrations, models
import nollesystemet.models.misc


class Migration(migrations.Migration):

    dependencies = [
        ('nollesystemet', '0008_feedback_210715'),
    ]

    operations = [
        migrations.AddField(
            model_name='nolleformanswer',
            name='special_needs',
            field=models.TextField(blank=True, validators=[nollesystemet.models.misc.validate_no_emoji]),
        ),
    ]
