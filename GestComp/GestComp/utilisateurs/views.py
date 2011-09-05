#!/usr/bin/env python
# -*- coding: utf-8 -*-
from GestComp.application.render2json import render_to_json
from GestComp.utilisateurs.models import Eleve, Groupe, Prof
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponse
import datetime

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


import csv
def analyse_maj_eleves(file,skip_first_line=False):
    '''
    Analyse un fichier CSV de mise àjour de la base élèves
    paramètres : file: fichier csv avec en première ligne les intitulés: (sconet)
        NOM PRENOM NE(E) LE DIV. DIV. PREC. 
    sortie: objet
         nb: nombre d'élèves traités
         pb: nombre de problèmes détectés
         nouveau: nombre de nouveaux élèves
         chgt_division: liste des élèves (avec id) changeant de division
         non_existant: liste des élèves non existants (donc à créer)
         pb_division: liste des élèves avec une erreur sur la division
         id_traites: liste des id des élèves traités
         id_pb : liste des id à problème
         
    ATTENTION: les élèves qui changent de nom ne sont pas reconnus 
    (l'eleve portant l'ancien nom est mis en actif=False et
    un nouvel élève est créé)
    '''
    #TODO: accepter d'autres intitulés, gérer le sexe
    #TODO: faire un vrai formulaire
         
        
        
    max=0
    titre=''
    liste=[]    
    nb=0
    no_pb=0
    pb=0
    nouveau=0
    with open(file,'rb') as f:
        reader=csv.DictReader(f)
        if skip_first_line:
            try:                
                reader.next()
            except StopIteration:
                return []
        
        non_existant=[]
        pb_division=[]
        chgt_division=[]
        id_traites=[]
        id_pb=[]
        encore=True
        while encore:
            try:
                next=reader.next()
            except StopIteration:
                next=[]
                encore=False
            else:
                el={}
                el['nom']=next['NOM'].lower()
                el['prenom']=next['PRENOM'].lower()
                nb+=1                
                try:
                    eleve=Eleve.objects.get(nom__iexact=next['NOM'],prenom__iexact=next['PRENOM'],
                                         groupe__grp_classe=True,groupe__nom=next['DIV. PREC.']
                                         )
                except:
                    # l'élève n'a pas été trouvé
                    print 'PB %s: ' % next['NOM']
                    try:
                        eleve=Eleve.objects.get(nom__iexact=next['NOM'],prenom__iexact=next['PRENOM'])
                    except:                     
                        # l'élève n'existe pas   
                        print 'non existant'
                        el['date_naissance']=next['NE(E) LE']
                        el['division']=next['DIV.']
                        non_existant.append(el)
                        nouveau+=1
                    else:
                        #l'élève existe mais n'est pas dans la bonne division
                        # problème à résoudre à la main                        
                        el['id']=eleve.id
                        el['division_prec']=next['DIV. PREC.']                        
                        print 'Prb de division',eleve.groupe_set.all()
                        pb+=1
                        pb_division.append(el)
                        id_pb.append(eleve.id)
                else:
                    #l'élève existe bien, il va falloir le mettre à jour
                    no_pb+=1    
                    el['id']=eleve.id
                    el['division']=next['DIV.']
                    el['division_prec']=next['DIV. PREC.']
                    chgt_division.append(el)
                    id_traites.append(eleve.id)
                liste.append(el)                
            
                
    return {'nb':nb,'pb':pb,'nouveau':nouveau,'no_pb':no_pb,
            'pb_division':pb_division,
            'non_existant':non_existant,
            'chgt_division':chgt_division,
            'id_traites':id_traites,
            'id_pb':id_pb}

from django.db import transaction
@transaction.commit_on_success  
def maj(file,maj_champs=False,**kwargs):
    result=analyse_maj_eleves(file)
    if result['pb']!=0:
        return {'success':False,'msg':'Erreurs à traiter prioritairement.','id_pb':result['id_pb']}
    tab_classe={}
    classes=Groupe.objects.filter(grp_classe=True)
    for classe in classes:
        tab_classe[classe.nom]=classe.id
    
    nb_chgt=0
    nb_creation=0
    nb_creation_div=0
    nb_sortants=0    
    #pas d'erreur, on y va
    
    #0 passage des autres elèves en passif
    sortants=Eleve.objects.extra(where=['id not in (%s)' % ','.join(str(i) for i in result['id_traites'])]).filter(actif=True)
    for eleve in sortants:
        eleve.actif=False
        eleve.save()
        nb_sortants+=1
    #1 changement de division
    
    for e in result['chgt_division']:
        eleve=Eleve.objects.get(id=e['id'])
        #on le sort des groupes
        eleve.groupe_set.clear()
        if e['division'] not in tab_classe.keys():
            # le groupe classe n'existe pas, on le crée
            nb_creation_div+=1
            g=Groupe.objects.create(nom=e['division'],grp_classe=True)
            tab_classe[g.nom]=g.id
        eleve.groupe_set.add(tab_classe[e['division']])
        nb_chgt+=1
        #if maj_champs:
            #mise à jour d'autres champs
            
    #2 creation des elèves
    for e in result['non_existant']:
        if e['division'] not in tab_classe.keys():
            # le groupe classe n'existe pas, on le crée
            g=Groupe.objects.create(nom=e['division'],grp_classe=True)
            tab_classe[g.nom]=g.id
            nb_creation_div+=1
        eleve=Eleve.create(nom=e['nom'],prenom=e['prenom'],
                           date_naissance=datetime.datetime.strptime(e['date_naissance'],'%d/%m/%Y')
                           )
        print 'eleve',e['nom'],eleve
        eleve.groupe_set.add(tab_classe[e['division']])
        nb_creation+=1
    return {"success":True,
            'nb_creation':nb_creation,
            'nb_chgt':nb_chgt,
            'nb_sortants':nb_sortants,
            'nb_creation_div':nb_creation_div}
    
