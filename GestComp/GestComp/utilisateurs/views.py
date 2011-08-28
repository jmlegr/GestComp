#!/usr/bin/env python
# -*- coding: utf-8 -*-
from GestComp.application.render2json import render_to_json
from GestComp.utilisateurs.models import Eleve, Groupe, Prof
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponse

@login_required
@render_to_json()
def infos_eleve_json(request):
    ''' retourne les infos sur l'élève request.POST['id']'''
    if ('id' in request.POST):
        eleve=Eleve.objects.get(id=request.POST['id'])
        response = HttpResponse()
        response.write(u'<p>Infos sur l\'élève:</p>')
        response.write(u'<p>Nom:<b>%s</b></p>'% eleve.nom)
        l={}
        l['nom']=eleve.nom
        l['truc']=2
        #return response
        return {'nom':eleve.nom}
    return HttpResponse('Aucune information')


@login_required
@render_to_json()
def liste_eleves_json(request):
    '''retourne la liste des eleves + la classe et les groupes'''
    eleves=Eleve.objects.filter(actif=True)
    #eleves=Eleve.objects.all()
    groupes=Groupe.objects.all()

    liste={}; liste_groupes=[]
    if (request.POST.has_key('action')):
        groupes_liste=(request.POST['action']=='groupes')
    for el in eleves:
        l={}
        l['nom']=el.nom
        l['prenom']=el.prenom
        l['classe']=''
        #if (groupes_liste): l['groupes']=[]
        #else: l['groupe']=''
        l['groupesliste']=[]
        l['groupes']=''
        
        l['id']=el.id
        liste[el.id]=l
       
    for g in groupes:
        liste_groupes.append({'id':g.id,'nom':g.nom,'classe':g.grp_classe})
        #for el in g.eleves.all():
        for el in g.eleves.filter(actif=True):
            if (g.grp_classe): 
                liste[el.id]['classe']=g.nom
            else:
                #if (groupes_liste): liste[el.id]['groupes'].append(g.nom)
                #else: liste[el.id]['groupes']+=g.nom+' - '
                liste[el.id]['groupesliste'].append(g.nom)
                liste[el.id]['groupes']+=g.nom+' - '
        #if (groupes_liste):
        #    for l in liste:
        #        liste[l]['groupes']=liste[l]['groupes'][3:-3]
   
    for l in liste:
        liste[l]['groupes']=liste[l]['groupes'][:-3]
    retour ={}
    retour['success']='true'
    retour['msg']='groupes'
    #retour['groupes']=liste_groupes
    retour['data']=[]
    retour_eleves=[]
    #for i in liste: retour['data'].append(liste[i])
    for i in liste: retour_eleves.append(liste[i])
    #retour['data'].append({'eleves':retour_eleves})
    #retour['data'].append({'groupes':liste_groupes})
    retour['data']=retour_eleves
    return retour

@login_required
@render_to_json()
def liste_groupes_json(request):
    ''' renvoit la liste des groupes
        seulement les groupes classe/non classe si classe existe
        en ajoutant '-' et 'aucun' si combo est vrai (pour listes combos...)
    '''
    combo=False
    if request.POST.has_key('combo'):
        combo=request.POST['combo']
        
    groupes=[]
        
    if combo :    groupes.append({'id':'-','nom':'-'})
    if (request.POST.has_key('classe')):
        groupes+=list(Groupe.objects.filter(grp_classe=(request.POST['classe']=='true')).order_by('nom').values('id','nom'))
    else:
        groupes+=list(Groupe.objects.all().order_by('nom').values('id','nom'))
    if combo: groupes.append({'id':'--','nom':'aucun'})
    
    retour={}
    retour['success']=True
    retour['data']=groupes
    return retour

@login_required
@render_to_json()
def liste_profs_json(request):
    ''' renvoit la liste des profs
        
        en ajoutant 'aucun' si combo est vrai (pour listes combos...)
        et 'administrateur' si admin est vrai
    '''
    combo=False
    admin=False
    if request.POST.has_key('combo'):
        combo=request.POST['combo']
    if request.POST.has_key('admin'):
        admin=request.POST['admin']
    profs=[]
        
    if combo :    profs.append({'id':'-','nom':'Aucun'})
    if admin :    profs.append({'id':'admin','nom':'Administrateur'})
    profs+=list(Prof.objects.all().order_by('nom').values('id','nom','prenom'))
    
    retour={}
    retour['success']=True
    retour['data']=profs
    return retour
 