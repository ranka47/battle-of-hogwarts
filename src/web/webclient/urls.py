"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import *

urlpatterns = [
   url(r'^$', 'src.web.webclient.views.webclient', name="index"),
   url(r'^admin$', 'src.web.webclient.views.webclientAdmin', name="admin")]
