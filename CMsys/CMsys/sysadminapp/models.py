from django.db import models
from django.conf import settings
from six import text_type
from six import python_2_unicode_compatible


@python_2_unicode_compatible
class SysAdmin(models.Model):
    """
    系统管理员信息：ID、账号、电话号码、密码、注册时间、更新时间
    """
    account = models.CharField(max_length=32, verbose_name='系统管理员账号')
    password = models.CharField(max_length=32, verbose_name='系统管理员密码')
    phone = models.CharField(max_length=32, verbose_name='系统管理员电话号码', null=True, blank=True, unique=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='管理员账号创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='管理员账号修改时间')

    class Meta:
        db_table = 'sysadmin'
        verbose_name = '系统管理员'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content
