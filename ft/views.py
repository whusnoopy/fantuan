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


def buildContext(filter_people=0,
                filter_restaurant=0,
                filter_pay_people=0,
                show_all=False,
                fantuan_date=''):
    pnames, peoples = fetchPeople()
    rnames = fetchRestaurant()

    table_head = {'list': ['时间', '地点', '总额', '人数', '人均', '付款', '团费']}
    table_head['people'] = []
    balance = {}
    cost = {}
    times = {}
    for pid, pactive in peoples.items():
        balance[pid] = 0
        cost[pid] = 0
        times[pid] = 0
        if show_all or pactive:
            table_head['people'].append({
                    'id': pid,
                    'name': pnames[pid],
            })

    all_month = {}
    table_lines = []
    sum_times = 0
    sum_cost = 0
    sum_count = 0

    deals = fetchDeals(pnames, rnames)
    for d in deals:
        m = d['date'].strftime("%Y%m")
        if m not in all_month:
            all_month[m] = 1

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
                line_people_detail['type'] = 'success'
            else:
                line_people_detail['cost'] = 0

            if pid == d['pay_people_id']:
                if pid in d['join_peoples']:
                    line_people_detail['cost'] = '%+.2f' % (d['charge'] - d['per_charge'])
                else:
                    line_people_detail['cost'] = '%+.2f' % d['charge']
                line_people_detail['type'] = 'danger'

            line_people_detail['balance'] = '=%.2f' % balance[pid]

            if show_all or pactive:
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
        if fantuan_date and (m != fantuan_date):
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

        line['date'] = d['date'].strftime("%Y-%m-%d %a")
        line['charge'] = '%.2f' % d['charge']
        line['per_charge'] = '%+.2f' % d['per_charge']
        line['fantuan_balance'] = '%.2f' % fantuan_balance
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
    stat_sum = [sum_cost, sum_count, '', '总额']
    stat_times = [sum_times, '', '', '次数']
    stat_avg = [sum_avg, sum_per_count, sum_per_avg, '平均']
    for pid, pactive in peoples.items():
        if show_all or pactive:
            avg = 0
            if times[pid]:
                avg = cost[pid] * 1.0 / times[pid]
            stat_sum.append('%.2f' % cost[pid])
            stat_times.append('%d' % times[pid])
            stat_avg.append('%.2f' % avg)

    context = Context({
            'this_month': fantuan_date,
            'date_list': sorted(list(all_month.keys()), reverse=True),
            'all_restaurant': sorted([{'id':k,'name':v} for k,v in rnames.items()]),
            'all_people': sorted([{'id':k,'name':v} for k,v in pnames.items()]),
            'table_head': table_head,
            'table_lines': table_lines,
            'stat_sum': stat_sum,
            'stat_times': stat_times,
            'stat_avg': stat_avg,
    })

    return context

def index(request):
    filter_people = 0
    if 'p' in request.GET:
        filter_people = int(request.GET['p'])

    filter_restaurant = 0
    if 'r' in request.GET:
        filter_restaurant = int(request.GET['r'])

    filter_pay_people = 0
    if 'pay' in request.GET:
        filter_pay_people = int(request.GET['pay'])

    show_all = 0
    if 'all' in request.GET:
        show_all = int(request.GET['all'])

    fantuan_date = datetime.now().strftime("%Y%m")
    if 'date' in request.GET:
        fantuan_date = request.GET['date']

    context = buildContext(
            filter_people=filter_people,
            filter_restaurant=filter_restaurant,
            filter_pay_people=filter_pay_people,
            show_all=show_all,
            fantuan_date=fantuan_date
        )

    return render(request, 'ft/index.html', context)
