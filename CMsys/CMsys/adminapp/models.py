# Create your models here.
from django.db import models
from django.conf import settings
from six import text_type
from six import python_2_unicode_compatible


# Create your models here.


@python_2_unicode_compatible
class Admin(models.Model):
    """
    管理员信息：ID、账号、电话号码、密码、注册时间、更新时间
    """
    account = models.CharField(max_length=32, verbose_name='管理员账号')
    password = models.CharField(max_length=32, verbose_name='管理员密码')
    phone = models.CharField(max_length=32, verbose_name='管理员电话号码', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='管理员账号创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='管理员账号修改时间')

    class Meta:
        db_table = 'admin'
        verbose_name = '管理员'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class Announcement(models.Model):
    title = models.CharField(max_length=128, verbose_name='公告标题')
    content = models.TextField(max_length=1024, verbose_name='公告内容')
    image = models.CharField(max_length=128, verbose_name='图片路径', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='公告创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='公告修改时间')

    publisher = models.ForeignKey(to='Admin', on_delete=models.SET_DEFAULT, default=0,
                                  related_name='announcement_checker', verbose_name='公告发布人')

    class Meta:
        db_table = 'announcement'
        verbose_name = '公告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class Question(models.Model):
    title = models.CharField(max_length=128, verbose_name='题目标题')
    content = models.TextField(max_length=1000, verbose_name='题目内容')
    image = models.CharField(max_length=128, verbose_name='图片路径', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='题目发布时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='题目修改时间')

    publisher = models.ForeignKey(to='Admin', on_delete=models.SET_DEFAULT, default=0,
                                  related_name='question_checker', verbose_name='题目发布人')

    class Meta:
        db_table = 'question'
        verbose_name = '题目'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class Certification(models.Model):
    content = models.TextField(max_length=1000, verbose_name='内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='证书上传时间')

    publisher = models.ForeignKey(to='Admin', on_delete=models.SET_DEFAULT, default=0,
                                  related_name='certification_uploader', verbose_name='证书上传者')
    team = models.ForeignKey(to='studentapp.Team', on_delete=models.SET_DEFAULT, default=0,
                             related_name='certification_downloader', verbose_name='获奖团队')

    class Meta:
        db_table = 'certification'
        verbose_name = '获奖证书'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class FilesModel(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    file = models.FileField(upload_to='uploads/')

    class Meta:
        db_table = 'files_storage'
        ordering = ['-id']
