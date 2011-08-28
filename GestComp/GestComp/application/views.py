#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseBadRequest
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import logout, authenticate, login
from django.template.context import RequestContext
from django.shortcuts import render_to_response
import simplejson
from django.core.serializers.json import DjangoJSONEncoder


def gestcomp_test(request):
    if request.user.is_authenticated():
        return render_to_response('test.html',RequestContext(request))
    else: 
        return gestcomp_login(request)

def gestcomp_index(request):
    if request.user.is_authenticated():
        return render_to_response('index.html',RequestContext(request))
    else: 
        return gestcomp_login(request)
@login_required
def gestcomp(request):
    if request.user.is_superuser: return HttpResponseRedirect('/admin')
    elif request.user.has_perm('application.est_prof'): return HttpResponseRedirect('/gestcomp/prof')
    elif request.user.has_perm('application.est_eleve'): return HttpResponseRedirect('/gestcomp/eleve')
    return HttpResponseBadRequest()
    

@permission_required('application.est_prof')
def gestcomp_prof(request):
    #connection à la page d'accueil prof    
    return HttpResponse('Page accueil <b>prof</b><p><a href="/test">tester</a>')

@permission_required('application.est_eleve')
def gestcomp_eleve(request):
    #connection à la page d'accueil élève
    return HttpResponse(u'Page accueil <b>élève</b>')


def gestcomp_login(request):
    #renvoie la page de login   

    return render_to_response('login.html',RequestContext(request))

def gestcomp_logout(request):
    logout(request)
    return HttpResponse(u'Logout réussi<p><a href="/gestcomp/login">se connecter</a>')

def ext_login(request):
    json = {
        'errors': {},
        'text': {},
        'success': False,
    }
    user = authenticate(username=request.POST['username'],
                        password=request.POST['password'])
    if user is not None:
        if user.is_active:            
            login(request, user)
            json['success'] = True
            #json['text']['welcome'] = 'Welcome, %s!' % (user.get_full_name(),)                     
            lien=''
            if user.is_superuser:
                lien='/admin'
            elif user.has_perm('application.est_prof'):
                lien='/index'
            elif user.has_perm('application.est_eleve'):
                lien='/gestcomp/eleve'
            else: 
                json['success']=False
                json['errors']={'username':u'ni élève ni prof...'}
            json['text']['lien']=lien
        else:
            # Return a 'disabled account' error message
            json['errors']['username'] = u'Compte désactivé.'
    else:
        # Return an 'invalid login' error message.
            json['errors']['username'] = u'utilisateur ou mot de passe invalide.'
            json['errors']['password']=u'utilisateur ou mot de passe invalide ici aussi'
    return HttpResponse(simplejson.dumps(json, cls=DjangoJSONEncoder))