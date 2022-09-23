from datetime import *
from django.db import models

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User

import geocoder
import os

from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class JobType(models.TextChoices):
  Permanent = 'Permanent'
  Temporary = 'Temporary'
  Internship = 'Internship'

class EducationType(models.TextChoices):
  Bachelors = 'Bachelors'
  Masters = 'Masters'
  Phd = 'Phd'

class IndustryType(models.TextChoices):
  Business = 'Business'
  IT = 'Information Technology'
  Banking = 'Banking'
  Education = 'Education'
  Telecommunications = 'Telecommunications'
  Other = 'Other'

class Experience(models.TextChoices):
  NO_EXPERIENCE = 'No Experience'
  ONE_YEAR = '1 Year'
  TWO_YEAR = '2 Years'
  THREE_YEAR_PLUS = '3 Years above'

def return_date_time():
  now = datetime.now()
  return now + timedelta(days=10)

class Job(models.Model):
  title = models.CharField(max_length=200, null=True, blank=True)
  description = models.TextField(null=True, blank=True)
  email = models.EmailField(null=True, blank=True)
  address = models.CharField(max_length=100, null=True, blank=True)
  job_type = models.CharField(max_length=10, choices=JobType.choices, default=JobType.Permanent)
  education = models.CharField(max_length=10, choices=EducationType.choices, default=EducationType.Bachelors)
  industry = models.CharField(max_length=30, choices=IndustryType.choices, default=IndustryType.Business)
  experience = models.CharField(max_length=20, choices=Experience.choices, default=Experience.THREE_YEAR_PLUS)
  salary = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(1000000)])
  positions = models.IntegerField(default=1)
  company = models.CharField(max_length=100, null=True, blank=True)
  point = gismodels.PointField(default=Point(0.0, 0, 0.0))
  last_date = models.DateTimeField(default=return_date_time)
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def save(self, *args, **kwargs):
    try:
      g = geocoder.mapquest(self.address, key=os.environ.get('GEOCODER_API_KEY'))

      print(g)

      lng = g.lng
      lat = g.lat

      self.point = Point(lng, lat)
      super(Job, self).save(*args, **kwargs)
    except Exception as e:
      print('--------->', e)
