from django.db import models
from django.conf import settings
from six import text_type
from six import python_2_unicode_compatible


# Create your models here.
@python_2_unicode_compatible
class Judge(models.Model):
    """
    评委信息：ID（django自动添加）、账号、密码、电话号码、注册时间、更新时间
    """
    account = models.CharField(max_length=32, verbose_name='评委账号')
    password = models.CharField(max_length=32, verbose_name='评委密码')
    phone = models.CharField(max_length=32, verbose_name='评委电话号码',  null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='评委账号创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='评委账号修改时间')

    class Meta:
        db_table = 'judge'
        verbose_name = '评委'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


