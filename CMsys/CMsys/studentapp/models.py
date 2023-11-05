import datetime

from django.db import models
from six import python_2_unicode_compatible


# Create your models here.

@python_2_unicode_compatible
class Team(models.Model):
    """
    队伍信息：ID（django自动添加）、队名、队长ID（外键）、邮寄地址、注册时间、更新时间
    """
    team_type_choices = (
        (1, '未提交作品'),
        (2, '已提交作品'),
        (3, '成绩已公布'),
    )

    team_type = models.IntegerField(choices=team_type_choices, default=1)
    name = models.CharField(max_length=32, verbose_name='团队名称', null=True, blank=True)
    address = models.CharField(max_length=100, verbose_name='邮寄地址')
    invite_number = models.CharField(max_length=64, verbose_name='邀请码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='团队创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='团队修改时间')

    leader = models.ForeignKey('Student', on_delete=models.SET_NULL, blank=True, null=True, related_name='team_leader',
                               verbose_name='队长')
    work = models.ForeignKey('Work', on_delete=models.SET_NULL, blank=True, null=True, related_name='team_work',
                             verbose_name='作品')

    class Meta:
        db_table = 'team'
        verbose_name = '团队信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


@python_2_unicode_compatible
class Student(models.Model):
    """
    学生信息：ID（django自动添加）、姓名、电话号码、密码、年龄、团队ID（外键）、注册时间、更新时间
    """
    student_type_choices = (
        (1, '未组队'),
        (2, '队员'),
        (3, '队长'),
    )

    student_type = models.IntegerField(choices=student_type_choices, default=1)
    name = models.CharField(max_length=32, verbose_name='学生姓名', null=True, blank=True)
    phone = models.CharField(max_length=32, verbose_name='学生电话号码', unique=True)
    password = models.CharField(max_length=64, verbose_name='学生密码')
    school = models.CharField(max_length=32, verbose_name='学生学校', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='学生账号创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='学生账号修改时间')

    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='team_member', verbose_name='团队成员')

    class Meta:
        db_table = 'student'
        verbose_name = '学生信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


@python_2_unicode_compatible
class Work(models.Model):
    """
    作品信息：ID（django自动添加）、队伍ID、评委ID、评分、注册时间、更新时间
    """
    grade = models.IntegerField(verbose_name='作品评分', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='作品提交时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='作品修改时间')
    description = models.CharField(max_length=255, verbose_name='作品简要描述', null=True, blank=True)
    accessory = models.CharField(blank=True, null=True, verbose_name='作品附件路径', max_length=128)

    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='work_team', verbose_name='团队作品')
    judge = models.ForeignKey('judgeapp.Judge', on_delete=models.DO_NOTHING, null=True, blank=True,
                              related_name='work_judge', verbose_name='评分评委')

    class Meta:
        db_table = 'work'
        verbose_name = '作品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class Recruitment(models.Model):
    """
    队长发布招募信息
    """
    title = models.CharField(verbose_name='标题', max_length=32)
    summary = models.CharField(verbose_name='简介', max_length=128)
    content = models.TextField(verbose_name='招募内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="招募信息发布时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name='招募信息更新时间')
    publisher = models.ForeignKey('studentapp.Student', on_delete=models.CASCADE,
                                  related_name='recruitment_student', verbose_name='招募信息发布者')

    class Meta:
        db_table = 'recruitment'
        verbose_name = '招募信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class Application(models.Model):
    applicant = models.ForeignKey('studentapp.Student', on_delete=models.CASCADE,
                                  related_name='application_student', verbose_name='申请人')
    content = models.TextField(verbose_name='申请内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="申请时间", null=True, blank=True)
    team = models.ForeignKey('studentapp.Team', on_delete=models.CASCADE,
                             related_name='application_team', verbose_name='申请的队伍')
    application_type_choices = (
        (1, '待处理'),
        (2, '通过'),
        (3, '不通过'),
    )
    application_type = models.IntegerField(choices=application_type_choices, default=1)

    class Meta:
        db_table = 'application'
        verbose_name = '入队申请信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content
