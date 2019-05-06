from django.conf.urls import url

from ft import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
