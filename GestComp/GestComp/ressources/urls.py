#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns

urlpatterns = patterns('ressources.views',
    (r'^prof','gestcomp_prof'),
    (r'^eleve','gestcomp_eleve'),
    (r'^login','gestcomp_login'),
    (r'^logout','gestcomp_logout'),
    
)