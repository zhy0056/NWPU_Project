# Generated by Django 3.2.12 on 2022-05-27 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0002_certification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='accessory',
            field=models.FileField(blank=True, max_length=128, null=True, upload_to='', verbose_name='附件路径'),
        ),
    ]
