from django.urls import path
from .views import *
from . import views
app_name = 'delivery'
urlpatterns = [
    path('test',views.test, name='test'),
    ]