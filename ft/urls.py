from django.conf.urls import patterns, url

from ft import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
