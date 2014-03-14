#!/usr/bin/python
# -*- coding: utf8 -*-

from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.db import connection

from ft.models import Restaurant, People, Deal


def fetchPeople():
  pnames = {}
  peoples = {}

  cursor = connection.cursor()
  cursor.execute("SELECT id, name, active FROM ft_people")

  for row in cursor.fetchall():
    pid = row[0]
    pnames[pid] = row[1].encode('utf8')
    peoples[pid] = row[2]

  return pnames, peoples


def fetchRestaurant():
  rnames = {}

  cursor = connection.cursor()
  cursor.execute("SELECT id, name FROM ft_restaurant")

  for row in cursor.fetchall():
    rnames[row[0]] = row[1].encode('utf8')

  return rnames


def fetchDeal2People():
  dp = {}

  cursor = connection.cursor()
  cursor.execute("SELECT deal_id, people_id FROM ft_deal_peoples")

  for row in cursor.fetchall():
    did = row[0]
    pid = row[1]
    if did not in dp:
      dp[did] = {}
    dp[did][pid] = 1

  return dp



def fetchDeals(pnames, rnames):
  dp = fetchDeal2People()
  deals = []

  cursor = connection.cursor()
  cursor.execute("SELECT id, restaurant_id, pay_people_id, deal_date, charge FROM ft_deal")

  for row in cursor.fetchall():
    nd = {
      'date': row[3],
      'restaurant_id': row[1],
      'restaurant': rnames[row[1]],
      'charge': row[4],
      'pay_people_id': row[2],
      'pay_people': pnames[row[2]],
    }
    if row[0] not in dp:
      nd['join_peoples'] = {}
      nd['people_count'] = 0
      nd['per_charge'] = 0
    else:
      nd['join_peoples'] = dp[row[0]]
      nd['people_count'] = len(nd['join_peoples'])
      nd['per_charge'] = nd['charge'] / nd['people_count']

    deals.append(dict(nd))

  deals.sort(key=lambda d:(d['date'], d['restaurant_id']))

  return deals


def buildContext(filter_people=0, filter_restaurant=0, filter_pay_people=0, active_only=True, show_all=False, end_date=None):
  if end_date:
    end_date = datetime.strptime(str(end_date), "%Y%m").replace(tzinfo=timezone.utc)
  else:
    end_date = timezone.now()

  start_date = end_date - timezone.timedelta(days=31)

  pnames, peoples = fetchPeople()
  rnames = fetchRestaurant()

  table_head = {'list': ['时间', '地点', '总额', '人数', '人均', '付款人', '团费']}
  table_head['people'] = []
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
          'name': pnames[pid],
      })

  table_lines = []
  sum_times = 0
  sum_cost = 0
  sum_count = 0

  trx = 0
  deals = fetchDeals(pnames, rnames)
  for d in deals:
    line = dict(d)
    line['peoples'] = []

    fantuan_balance = 0
    people_join = False
    balance[d['pay_people_id']] += d['charge']
    for pid, pactive in peoples.items():
      line_people_detail = {}

      if pid in d['join_peoples']:
        balance[pid] -= d['per_charge']
        line_people_detail['cost'] = '%+.2f' % -d['per_charge']
        line_people_detail['type'] = 'jointd'
      else:
        line_people_detail['cost'] = 0

      if pid == d['pay_people_id']:
        if pid in d['join_peoples']:
          line_people_detail['cost'] = '%+.2f' % (d['charge'] - d['per_charge'])
        else:
          line_people_detail['cost'] = '%+.2f' % d['charge']
        line_people_detail['type'] = 'paytd'

      line_people_detail['balance'] = '=%.2f' % balance[pid]

      if not active_only or pactive:
        line['peoples'].append(line_people_detail)

      if pid == filter_people and (pid in d['join_peoples'] or pid == d['pay_people_id']):
        people_join = True

      fantuan_balance += balance[pid]
    # end for pid

    if filter_people and (not people_join):
      continue
    if filter_restaurant and (filter_restaurant != d['restaurant_id']):
      continue
    if filter_pay_people and (filter_pay_people != d['pay_people_id']):
      continue
    if not show_all and (d['date'] < start_date or d['date'] > end_date):
      continue

    # 充值\提现\转账不记录在消费记录里
    if d['people_count'] > 1:
      for pid in peoples.keys():
        if pid in d['join_peoples']:
          times[pid] += 1
          cost[pid] += d['per_charge']
      sum_times += 1
      sum_cost += d['charge']
      sum_count += len(d['join_peoples'])

    line['date'] = d['date'].strftime("%Y %m-%d")
    line['charge'] = '%+.2f' % d['charge']
    line['per_charge'] = '%+.2f' % d['per_charge']
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
  context = buildContext()
  return render(request, 'ft/index.html', context)

def people(request, people_id):
  context = buildContext(filter_people=int(people_id))
  return render(request, 'ft/index.html', context)

def restaurant(request, restaurant_id):
  context = buildContext(filter_restaurant=int(restaurant_id))
  return render(request, 'ft/index.html', context)

def pay_people(request, pay_people_id):
  context = buildContext(filter_pay_people=int(pay_people_id))
  return render(request, 'ft/index.html', context)

def show_all(request):
  context = buildContext(active_only=False, show_all=True)
  return render(request, 'ft/index.html', context)

def end_date(request, end_date):
  context = buildContext(end_date=int(end_date))
  return render(request, 'ft/index.html', context)
