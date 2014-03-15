from django.conf.urls import patterns, url

from ft import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^all/$', views.show_all, name='show_all'),
    url(r'^history/(?P<start_date>\d+)/$', views.start_date, name='start_date'),
    url(r'^before/(?P<end_date>\d+)/$', views.end_date, name='end_date'),
    url(r'^people/(?P<people_id>\d+)/$', views.people, name='people'),
    url(r'^restaurant/(?P<restaurant_id>\d+)/$', views.restaurant, name='restaurant'),
    url(r'^pay_people/(?P<pay_people_id>\d+)/$', views.pay_people, name='pay_people'),
)
