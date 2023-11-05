# Generated by Django 3.2.12 on 2022-05-19 06:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0008_remove_recruitment_comment_count'),
        ('adminapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=1000, verbose_name='内容')),
                ('accessory', models.CharField(blank=True, max_length=128, null=True, verbose_name='证书附件路径')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='证书上传时间')),
                ('publisher', models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='certification_uploader', to='adminapp.admin', verbose_name='证书上传者')),
                ('team', models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='certification_downloader', to='studentapp.team', verbose_name='获奖团队')),
            ],
            options={
                'verbose_name': '获奖证书',
                'verbose_name_plural': '获奖证书',
                'db_table': 'certification',
            },
        ),
    ]
