# Generated by Django 3.2.12 on 2022-05-11 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0004_application_create_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='student_type',
            field=models.IntegerField(choices=[(1, '待处理'), (2, '通过'), (3, '不通过')], default=1),
        ),
    ]
