#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns

urlpatterns = patterns('evaluations.views',
    (r'^creationEvaluation','creation_evaluation'),
    (r'^liste_aides','liste_aides'),
    (r'^liste_evaluations','liste_evaluations'),
    (r'^resultats_eval$','resultats_eval'),
    (r'^modif_resultats','modif_resultats'),
    (r'^validation_directe','validation_directe'),
    (r'^resultats_eleve','resultats_eleve'),
    (r'^modif_evaluation','modif_evaluation'),
    (r'^stores','stores'),
    (r'^resultats_evaluations','resultats_evaluations'),
)