#!/usr/bin/python
# -*- coding: utf8 -*-

from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.template import Context

from ft.models import Restaurant, People, Deal

def buildContext(deals, filter_people=0, filter_restaurant=0, filter_pay_people=0, active_only=True, show_all=False, end_date=None):
  if end_date:
    end_date = datetime.strptime(str(end_date), "%Y%m").replace(tzinfo=timezone.utc)
  else:
    end_date = timezone.now()

  start_date = end_date - timezone.timedelta(days=31)

  table_head = {'list': ['时间', '地点', '总额', '人数', '人均', '付款人', '团费']}
  table_head['people'] = []
  peoples = dict([(p.id, p.active) for p in People.objects.all()])
  pnames = dict([(p.id, p.name) for p in People.objects.all()])
  balance = {}
  cost = {}
  times = {}
  for pid, pactive in peoples.items():
    balance[pid] = 0
    cost[pid] = 0
    times[pid] = 0
    if not active_only or pactive:
      table_head['people'].append({
          'id': pid,
          'name': pnames[pid].encode('utf8'),
      })

  table_lines = []
  sum_times = 0
  sum_cost = 0
  sum_count = 0

  trx = 0
  for d in deals:
    deal_peoples_id = dict([(p.id, 1) for p in d.peoples.all()])
    charge = d.charge
    deal_per_charge = d.per_charge()
    pay_id = d.pay_people.id
    pay_people = d.pay_people.name

    line = {}
    line['date'] = d.deal_date.strftime("%Y-%m-%d")
    line['restaurant_id'] = d.restaurant.id
    line['restaurant'] = d.restaurant.name.encode('utf8')
    line['charge'] = charge
    line['people_count'] = len(deal_peoples_id)
    line['per_charge'] = '%.2f' % deal_per_charge
    line['pay_people_id'] = pay_id
    line['pay_people'] = pay_people.encode('utf8')
    line['peoples'] = []
    fantuan_balance = 0

    people_join = False
    balance[pay_id] += charge
    pidx = 0
    for pid, pactive in peoples.items():
      pidx += 1
      if pid == filter_people and (pid in deal_peoples_id or pid == pay_id):
        people_join = True
      lp = {}
      if pid in deal_peoples_id:
        balance[pid] -= deal_per_charge
        lp['cost'] = '%+.2f' % -deal_per_charge
        lp['type'] = 'jointd'
      else:
        lp['cost'] = 0
      if pid == pay_id:
        if pid in deal_peoples_id:
          lp['cost'] = '%+.2f' % (charge - deal_per_charge)
        else:
          lp['cost'] = '%+.2f' % charge
        lp['type'] = 'paytd'
      lp['balance'] = '=%.2f' % balance[pid]
      if not active_only or pactive:
        line['peoples'].append(lp)
      fantuan_balance += balance[pid]

    if filter_people and (not people_join):
      continue
    if filter_restaurant and (filter_restaurant != d.restaurant.id):
      continue
    if filter_pay_people and (filter_pay_people != pay_id):
      continue
    if not show_all and (d.deal_date < start_date or d.deal_date > end_date):
      continue

    # 充值\提现\转账不记录在消费记录里
    if d.peoples.count() > 1:
      for pid in peoples.keys():
        if pid in deal_peoples_id:
          times[pid] += 1
          cost[pid] += deal_per_charge
      sum_times += 1
      sum_cost += charge
      sum_count += len(deal_peoples_id)

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
  for pid, pactive in peoples.items():
    if not active_only or pactive:
      avg = 0
      if times[pid]:
        avg = cost[pid] * 1.0 / times[pid]
      stat_sum.append('%.2f' % cost[pid])
      stat_times.append('%d' % times[pid])
      stat_avg.append('%.2f' % avg)

  next_date = end_date - timezone.timedelta(days=1)
  context = Context({
      'end_date': datetime.strftime(next_date, '%Y%m'),
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

def show_all(request):
  deals = Deal.objects.order_by('deal_date', 'restaurant')
  context = buildContext(deals, active_only=False, show_all=True)
  return render(request, 'ft/index.html', context)

def end_date(request, end_date):
  deals = Deal.objects.order_by('deal_date', 'restaurant')
  context = buildContext(deals, end_date=int(end_date))
  return render(request, 'ft/index.html', context)
