#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns

urlpatterns = patterns('utilisateurs.views',
    (r'^liste_eleves','liste_eleves_json'),
    (r'^liste_groupes','liste_groupes_json'),
    (r'^liste_profs','liste_profs_json'),
    (r'^infos_eleve','infos_eleve_json'),
    )