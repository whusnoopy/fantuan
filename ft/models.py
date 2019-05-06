#!/usr/bin/python
# -*- coding:utf-8 -*-

from django.db import models
from django.utils import timezone

# Create your models here.

class Restaurant(models.Model):
  name = models.CharField(max_length=200, verbose_name="餐厅名", unique=True)

  class Meta:
    verbose_name = '餐厅'

  def __unicode__(self):
    return self.name

class People(models.Model):
  name = models.CharField(max_length=200, verbose_name="姓名", unique=True)
  active = models.NullBooleanField(default=1, verbose_name="活跃用户")

  class Meta:
    verbose_name = '人'

  def __unicode__(self):
    return self.name
 
class Deal(models.Model):
  restaurant = models.ForeignKey(Restaurant, verbose_name="餐厅")
  pay_people = models.ForeignKey(People, verbose_name="付款人", help_text="转账时此处选转出人下面参与人只选转入人")
  deal_date = models.DateTimeField('date dealed', default=timezone.now, help_text="为避免 django 框架时区处理错误, 时间请统一选中午")
  charge = models.FloatField(default=0, verbose_name="消费", help_text="消费或转账金额, 统一用正数")
  peoples = models.ManyToManyField(People, related_name='join+', blank=True)

  class Meta:
    verbose_name = '消费记录'
    ordering = ['deal_date']

  def __unicode__(self):
    return self.pay_people.name + " paid " + \
            str(self.charge) + " at " + \
            self.restaurant.name + " on " + \
            self.deal_date.strftime("%Y-%m-%d")

  def get_peoples(self):
    return '\n'.join([p.name for p in self.peoples.all()])

  def per_charge(self):
    if self.peoples.count():
      return self.charge / self.peoples.count()
    else:
      return 0

