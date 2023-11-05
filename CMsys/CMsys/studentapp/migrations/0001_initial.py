# Generated by Django 3.2.12 on 2022-05-10 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('judgeapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_type', models.IntegerField(choices=[(1, '未组队'), (2, '队员'), (3, '队长')], default=1)),
                ('name', models.CharField(max_length=32, verbose_name='学生姓名')),
                ('phone', models.CharField(max_length=32, unique=True, verbose_name='学生电话号码')),
                ('password', models.CharField(max_length=64, verbose_name='学生密码')),
                ('age', models.IntegerField(verbose_name='学生年龄')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='学生账号创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='学生账号修改时间')),
            ],
            options={
                'verbose_name': '学生信息',
                'verbose_name_plural': '学生信息',
                'db_table': 'student',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_type', models.IntegerField(choices=[(1, '未报名参赛'), (2, '已报名参赛')], default=1)),
                ('name', models.CharField(max_length=32, verbose_name='团队名称')),
                ('address', models.CharField(max_length=100, verbose_name='邮寄地址')),
                ('invite_number', models.CharField(max_length=64, verbose_name='邀请码')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='团队创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='团队修改时间')),
                ('leader', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_leader', to='studentapp.student', verbose_name='队长')),
            ],
            options={
                'verbose_name': '团队信息',
                'verbose_name_plural': '团队信息',
                'db_table': 'team',
            },
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.IntegerField(blank=True, null=True, verbose_name='作品评分')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='作品提交时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='作品修改时间')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='作品简要描述')),
                ('accessory', models.CharField(blank=True, max_length=128, null=True, verbose_name='作品附件路径')),
                ('judge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='work_judge', to='judgeapp.judge', verbose_name='评分评委')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_team', to='studentapp.team', verbose_name='团队作品')),
            ],
            options={
                'verbose_name': '作品',
                'verbose_name_plural': '作品',
                'db_table': 'work',
            },
        ),
        migrations.AddField(
            model_name='team',
            name='work',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_work', to='studentapp.work', verbose_name='作品'),
        ),
        migrations.AddField(
            model_name='student',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_member', to='studentapp.team', verbose_name='团队成员'),
        ),
        migrations.CreateModel(
            name='Recruitment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='标题')),
                ('summary', models.CharField(max_length=128, verbose_name='简介')),
                ('content', models.TextField(verbose_name='招募内容')),
                ('comment_count', models.IntegerField(default=0, verbose_name='评论数')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='招募信息发布时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='招募信息更新时间')),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recruitment_student', to='studentapp.student', verbose_name='招募信息发布者')),
            ],
            options={
                'verbose_name': '招募信息',
                'verbose_name_plural': '招募信息',
                'db_table': 'recruitment',
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='申请内容')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='application_student', to='studentapp.student', verbose_name='申请人')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='application_team', to='studentapp.team', verbose_name='申请的队伍')),
            ],
            options={
                'verbose_name': '入队申请信息',
                'verbose_name_plural': '入队申请信息',
                'db_table': 'application',
            },
        ),
    ]
