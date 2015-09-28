"""
Definition of models.
"""

from django.db import models

# Create your models here.
class FlowQueryLog(models.Model):
	time = models.DateTimeField()
	download = models.BigIntegerField()
	upload = models.BigIntegerField()
	total = models.BigIntegerField()
	note = models.CharField(max_length=100)
