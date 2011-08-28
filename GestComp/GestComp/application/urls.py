#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns

urlpatterns = patterns('application.views',
    (r'^$','gestcomp'),
    (r'^prof','gestcomp_prof'),
    (r'^eleve','gestcomp_eleve'),
    (r'^login','gestcomp_login'),
    (r'^logout','gestcomp_logout'),
    (r'^ext_login','ext_login'),
    
)