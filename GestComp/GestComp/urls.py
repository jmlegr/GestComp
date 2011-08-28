#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^accounts/login/$',  'application.views.gestcomp_login'),
    (r'^gestcomp/', include('application.urls')),
    (r'^utilisateurs/',include('utilisateurs.urls')),
    (r'^competences/',include('competences.urls')),
    (r'^evaluations/',include('evaluations.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^smedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        (r'^test1',direct_to_template,{'template':'test1.html'}),
        #(r'^index',direct_to_template,{'template':'index.html'}),
        (r'^index','application.views.gestcomp_index'),
        #(r'^test',direct_to_template,{'template':'test.html'}),
        (r'^test','application.views.gestcomp_test'),
        (r'^eval',direct_to_template,{'template':'testeval.html'}),
)
