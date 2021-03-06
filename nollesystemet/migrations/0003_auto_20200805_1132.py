# Generated by Django 3.0.8 on 2020-08-05 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nollesystemet', '0002_happeninginfo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='happeninginfo',
            name='payment_info',
        ),
        migrations.AddField(
            model_name='happeninginfo',
            name='payment_info_html',
            field=models.TextField(blank=True, verbose_name='Betalningsinformation (HTML)'),
        ),
        migrations.AddField(
            model_name='happeninginfo',
            name='payment_info_plain_text',
            field=models.TextField(blank=True, verbose_name='Betalningsinformation (Plain text)'),
        ),
    ]
