from django.conf.urls import url, include
from rest_framework import routers

from adoption import views

router = routers.DefaultRouter()
router.register('post', views.PostView, basename='post')

urlpatterns = [

] + router.urls