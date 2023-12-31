# Generated by Django 3.2.12 on 2022-05-10 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SysAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=32, verbose_name='系统管理员账号')),
                ('password', models.CharField(max_length=32, verbose_name='系统管理员密码')),
                ('phone', models.CharField(blank=True, max_length=32, null=True, unique=True, verbose_name='系统管理员电话号码')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='管理员账号创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='管理员账号修改时间')),
            ],
            options={
                'verbose_name': '系统管理员',
                'verbose_name_plural': '系统管理员',
                'db_table': 'sysadmin',
            },
        ),
    ]
