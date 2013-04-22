from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from ft.models import Restaurant, People, Deal

admin.site.register(Restaurant)
admin.site.register(People)

class DealAdmin(admin.ModelAdmin):
  filter_horizontal = ('peoples',)
  list_display = ('deal_date', 'restaurant', 'charge', 'pay_people', 'per_charge', 'get_peoples')
  list_filter = ['restaurant', 'pay_people']
  list_per_page = 30
  ordering = ('-deal_date',)
  date_hierarchy = 'deal_date'

admin.site.register(Deal, DealAdmin)
