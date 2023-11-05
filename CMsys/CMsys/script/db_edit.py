import os, django, sys
from judgeapp import models

# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../../..')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CMsys.settings")
django.setup()

models.Judge.objects.create(account="123456", password="zhy200056", phone="15577775555")
