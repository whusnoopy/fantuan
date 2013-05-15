#!/usr/bin/python
# -*- coding: utf8 -*-

from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.template import Context

from ft.models import Restaurant, People, Deal

def buildContext(deals, filter_people=0, filter_restaurant=0, filter_pay_people=0):
  table_head = {'list': ['时间', '地点', '总额', '人数', '人均', '付款人', '团费']}
  table_head['people'] = []
  peoples = People.objects.all()
  balance = {}
  cost = {}
  times = {}
  for p in peoples:
    balance[p] = 0 
    cost[p] = 0
    times[p] = 0
    table_head['people'].append({
        'id': p.id,
        'name': p.name.encode('utf8'),
    })

  table_lines = []
  sum_times = 0
  sum_cost = 0
  sum_count = 0

  trx = 0
  for d in deals:
    line = {}
    line['date'] = d.deal_date.strftime("%Y-%m-%d")
    line['restaurant_id'] = d.restaurant.id
    line['restaurant'] = d.restaurant.name.encode('utf8')
    line['charge'] = d.charge
    line['people_count'] = d.peoples.count()
    line['per_charge'] = '%.2f' % d.per_charge()
    line['pay_people_id'] = d.pay_people.id
    line['pay_people'] = d.pay_people.name.encode('utf8')
    line['peoples'] = []
    fantuan_balance = 0

    people_join = False
    balance[d.pay_people] += d.charge
    for p in peoples:
      if p.id == filter_people and (p in d.peoples.all() or p == d.pay_people):
        people_join = True
      lp = {}
      if p in d.peoples.all():
        balance[p] -= d.per_charge()
        lp['cost'] = '%+.2f' % -d.per_charge()
        lp['type'] = 'jointd'
      else:
        lp['cost'] = 0
      if p.id == d.pay_people.id:
        if p in d.peoples.all():
          lp['cost'] = '%+.2f' % (d.charge - d.per_charge())
        else:
          lp['cost'] = '%+.2f' % d.charge
        lp['type'] = 'paytd'
      lp['balance'] = '=%.2f' % balance[p]
      line['peoples'].append(lp)
      fantuan_balance += balance[p]

    if filter_people and (not people_join):
      continue
    if filter_restaurant and (filter_restaurant != d.restaurant.id):
      continue
    if filter_pay_people and (filter_pay_people != d.pay_people.id):
      continue

    for p in peoples:
      if p in d.peoples.all():
        times[p] += 1
        cost[p] += d.per_charge()
    if d.peoples.count():
      sum_times += 1
      sum_cost += d.charge
      sum_count += d.peoples.count()
    line['fantuan_balance'] = '%.2f' % fantuan_balance
    trx += 1
    if trx % 2:
      line['type'] = 'tro'
    else:
      line['type'] = 'tre'
    table_lines.append(line)

  if sum_count:
    sum_avg = '%.2f' % (sum_cost * 1.0 / sum_times)
    sum_per_count = '%.2f' % (sum_count * 1.0 / sum_times)
    sum_per_avg = '%.2f' % (sum_cost * 1.0 / sum_count)
  else:
    sum_avg = 0
    sum_per_count = 0
    sum_per_avg = 0

  # statistics
  stat_sum = ['', '', sum_cost, sum_count, '', '总额', '']
  stat_times = ['', '', sum_times, '', '', '次数', '']
  stat_avg = ['', '', sum_avg, sum_per_count, sum_per_avg, '平均', '']
  for p in peoples:
    avg = 0
    if times[p]:
      avg = cost[p] * 1.0 / times[p]
    stat_sum.append('%.2f' % cost[p])
    stat_times.append('%d' % times[p])
    stat_avg.append('%.2f' % avg)

  context = Context({
      'table_head': table_head,
      'table_lines': table_lines,
      'stat_sum': stat_sum,
      'stat_times': stat_times,
      'stat_avg': stat_avg,
  })

  return context

def index(request):
  deals = Deal.objects.order_by('deal_date', 'restaurant')
  context = buildContext(deals)
  return render(request, 'ft/index.html', context)

def people(request, people_id):
  deals = Deal.objects.order_by('deal_date', 'restaurant')
  context = buildContext(deals, filter_people=int(people_id))
  return render(request, 'ft/index.html', context)

def restaurant(request, restaurant_id):
  deals = Deal.objects.order_by('deal_date', 'restaurant')
  context = buildContext(deals, filter_restaurant=int(restaurant_id))
  return render(request, 'ft/index.html', context)

def pay_people(request, pay_people_id):
  deals = Deal.objects.order_by('deal_date', 'restaurant')
  context = buildContext(deals, filter_pay_people=int(pay_people_id))
  return render(request, 'ft/index.html', context)
