# Generated by Django 3.2.12 on 2022-05-10 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Judge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=32, verbose_name='评委账号')),
                ('password', models.CharField(max_length=32, verbose_name='评委密码')),
                ('phone', models.CharField(blank=True, max_length=32, null=True, verbose_name='评委电话号码')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='评委账号创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='评委账号修改时间')),
            ],
            options={
                'verbose_name': '评委',
                'verbose_name_plural': '评委',
                'db_table': 'judge',
            },
        ),
    ]
