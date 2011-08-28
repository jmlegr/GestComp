#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib.auth import logout

@permission_required('ressources.est_prof')
def gestcomp_prof(request):
    #connection à la page d'accueil prof
     return HttpResponse('Page accueil <b>prof</b>')

@permission_required('ressources.est_eleve')
def gestcomp_eleve(request):
    #connection à la page d'accueil élève
    return HttpResponse(u'Page accueil <b>élève</b>')

def gestcomp_login(request):
    #renvoie la page de login
    return HttpResponse(u'Page accueil <b>login</b>')

def gestcomp_logout(request):
    logout(request)
    return HttpResponse(u'Logout réussi')
