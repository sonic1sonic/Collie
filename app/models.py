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

class AccountAP(models.Model):
	time = models.DateTimeField()
	username = models.CharField(max_length=100)
	password = models.CharField(max_length=100)