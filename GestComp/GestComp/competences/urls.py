#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns

urlpatterns = patterns('competences.views',
    (r'^liste_competences','liste_competences_json'),
    (r'^retourbranche','retour_branche'),
    #(r'^test','test'),
    (r'^modif_liens','modif_liens'),
    (r'^supprime_liens','supprime_liens'), 
    (r'^initgraphe','initialise_graphe'), 
    (r'^supprime_graphe','supprime_graphe'),  
    (r'^renommer_competence','renommer_competence'),
    (r'^ajout_competence','ajout_competence'),
    (r'^supprime_competence','supprime_competence'),
    (r'^change_user','change_user'),
    (r'^infos_competence','infos_competence_json'),
)
