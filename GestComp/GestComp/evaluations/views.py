#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 
 *  $Revision$
 * Dernière modification $Date$
''' 

from GestComp.application.render2json import render_to_json
from GestComp.evaluations.models import Plan_evaluation, Evaluation,\
    Competence_a_evaluer, Competence_aide, Competence_evaluee
from GestComp.settings import DEBUT_ANNEE
import datetime
from GestComp.utilisateurs.models import Eleve
from decimal import Decimal
from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q
import logging
from GestComp.competences.models import Competence, Graphe_competences
import simplejson
from django.core.exceptions import ValidationError
import decimal
from django.contrib.auth.models import User
import sys
from django.db import models, transaction, connection
from GestComp.ressources.request import is_true
from django.http import HttpResponse


@login_required()
@render_to_json()
def stores(request):
    '''renvoie les dicts de base'''
    if ('type' in request.POST):
        if (request.POST['type']=='aides'):           
            if (request.POST.has_key('action')):
                if request.POST['action']=='tous':
                    aides=list(Competence_aide.objects.select_related('user').all().order_by('nom').values('id','nom','description','user'))
                elif request.POST['action']=='perso':
                    aides=list(Competence_aide.objects.filter(user=request.user).order_by('nom').values('id','nom','description','user'))
                aides.insert(0,{'id':-1,'nom':'aucune'})
                return {'success':True,'data':aides}
    return {'success':False,'errorMessage':u'Mauvais formatage de la demande'}

@login_required()
@render_to_json()
def liste_aides(request):
    ''' renvoit la liste des type d'aides
        seulement les types persos : action='perso'
        toutes si action='tout'         
    '''
    if not request.user.has_perm('application.est_prof'):
        return {'succes':False,'errorMessage':u'Accès non autorisé.'}
    
    if (request.POST.has_key('action')):
        if request.POST['action']=='tout':
            aides=list(Competence_aide.objects.all().order_by('nom').values('id','nom','description','user'))
        elif request.POST['action']=='perso':
            aides=list(Competence_aide.objects.filter(user=request.user).order_by('nom').values('id','nom','description','user'))
        aides.append({'id':-1,'nom':'aucune'})
        return {'success':True,'data':aides}
    return {'succes':False,'errorMessage':u'Mauvais formatage de la demande'}


def creer_comps_eval(eleve,evaluation,comps_a_eval):
    """ cré une copie d'un queryset competence_a_evaluer 
    dans une liste de competence_evaluee, mixé avec les competence_evaluee deja existantes
    """
    cp=Competence_evaluee.objects.filter(eleve=eleve,evaluation=evaluation).order_by('numero')
    l=[]
    for c in comps_a_eval:
        try:
            comp_eval=cp.get(competence=c.competence,numero=c.numero)
        except Competence_evaluee.DoesNotExist:
            #calcul du barême
            if c.bareme:
                bareme=c.bareme
            else:
                bareme=c.items
                
            comp_eval=Competence_evaluee(eleve=eleve,
                                     competence=c.competence,
                                     evaluation=evaluation,
                                     numero=c.numero,
                                     methode=c.methode,
                                     items=c.items,
                                     detail=c.detail,
                                     statut=c.statut,
                                     a_note=evaluation.a_note and c.a_note,
                                     bareme=bareme,
                                     coefficient=evaluation.coefficient  ,
                                     mode=c.mode,
                                     type_eval=c.type_eval,
                                     aide=c.aide,
                                     type_aide=c.type_aide,
                                     option=c.option,
                                     user=c.user                                  
                                     )
            comp_eval.save()
        except:
            raise NameError('Erreur inconnue')
        l.append(comp_eval)
    return l

@render_to_json()
def creation_evaluation(request):
    # création de l'évaluation
    fields=request.POST
    if 'fieldNbCompetences' not in fields or 'fieldNom' not in fields:
        return {'success':False,'errorMessage':'Champs requis absents.',
                'errors':[{'id':'fieldCompetences','msg':'Champs obligatoire'},
                          {'id':'fieldNom','msg':'Champs Obligatoire'}]
                }
    # les competences sont obligatoires
    if fields['fieldNbCompetences']=='' or fields['fieldNbCompetences']=='0':
        return {'success':False,'errorMessage':u'Vous devez choisir <i>au moins une compétence</i> à évaluer.'}
    #tempo:les eleves sont obligatoires
    if fields['fieldEleves']=='':
        return {'success':False,'errorMessage':u'Vous devez choisir <i>au moins un élève</i> à évaluer.'}
    #verification de l'existence d'un plan de mmeme nom et meme user
    
    plan,created=Plan_evaluation.objects.get_or_create(nom=request.POST['fieldNom'],user=request.user,date_modification__gt=DEBUT_ANNEE)
    if not created :
        #le plan existe déjà
        return {"success":False,'errorMessage':u'Vous avez déjà créé un plan portant ce nom "%s"' %request.POST['fieldNom'],
                'errors':[{'id':'fieldNom','msg':'Plan existant'}]}
    
    logging.debug('plan créé')
    
    #instanciation du nouveau plan
    
    #test si prof : 2 possibilités:
    # celle-ci pose un problème : détecte les profs ET les superadmin non profs
    #    if request.user.has_perm('application.est_prof'):
    #donc on vérifie seulement s'il ya une clé de prof vers user.
    #inconvénient:fonctionne meme avec un compte inactif, et on touche la base
    #    if request.user.prof_set.all():
    #d'où l'alternative:
    if not request.user.is_superuser:
        if request.user.has_perm('application.est_prof'): 
            plan.prof=request.user.prof_set.all()[0]      
        else:     
            plan.delete()       
            return {'success':False,'errorMessage':u'Vous n\'êtes pas enseignant, impossible de créer un plan.'}
    
    '''TODO: adapter  ca pour les modifications
        if not change:
            obj.user = request.user
            if obj.prof==None and is_prof(obj.user) and not is_admin(obj.user):
                obj.prof=Prof.objects.get(user=obj.user)
            obj.save()
        elif request.user.is_superuser or obj.user == request.user:
            obj.save()
        else:
            request.user.message_set.create(message=u"Le plan %s n'a pas été changé (vous n'êtes pas le créateur de ce plan)" % obj.nom)
            return False
    '''
        
    logging.debug('fields:')
    if ('fieldType' in fields): plan.type=fields['fieldType']
    if ('fieldMode' in fields): plan.mode=fields['fieldMode']
    if ('fieldMethode' in fields): plan.mode=fields['fieldMethode']
    plan.a_note='fieldNote' in fields    
    plan.public='fieldPublic' in fields
     
    #creation de l'évaluation liée
    eval,created=Evaluation.objects.get_or_create(nom=fields['fieldNom'],user=request.user,date_modification__gt=DEBUT_ANNEE)
    if not created:
        plan.delete()
        return {"success":False,'errorMessage':u'Vous avez déjà créé une évaluation portant ce nom "%s"' %fields['fieldNom'] ,
                'errors':[{'id':'fieldNom','msg':'Plan existant'}]}
    eval.plan_evaluation=plan
    if fields['fieldDescription']!='':
        plan.description=u"(plan créé automatiquement par l\'évaluation du même nom)"+fields['fieldDescription']
        eval.description=fields['fieldDescription']
    plan.aide='fieldAide' in fields
    eval.aide='fieldAide' in fields
    if ('fieldTypeAide' in fields) and (fields['fieldTypeAide']!=''): 
        plan.type_aide_id=int(fields['fieldTypeAide'])
        eval.type_aide_id=int(fields['fieldTypeAide'])  
    if fields['fieldRemarquesAide']!='': 
        plan.remarques=u"(plan créé automatiquement par l\'évaluation du même nom)"+fields['fieldRemarquesAide']
        eval.remarques=fields['fieldRemarquesAide']
    eval.a_note='fieldNote' in fields
    eval.points_max=fields['fieldNoteSur']
    if 'fieldNoteSur' in fields: eval.points_max=Decimal(fields['fieldNoteSur']) 
    if 'fieldNoteCoef' in fields: eval.coefficient=Decimal(fields['fieldNoteCoef'])
    if fields['fieldDate']!='':
        #TODO : changement auto du format de date?
        eval.date_evaluation=datetime.datetime.strptime(fields['fieldDate'],'%d/%m/%y')
    if fields['fieldEleves']=='':
        #plan.save()
        #eval.save()
        #return {'success':True,'errorMessage':u'Attention : pas d\'élève!', 'msg':u'''<b style="text-align:center">Attention</b>: l'évaluation a été créée <b>SANS ELEVE</b>. 
         #               <p><i>Vous devrez modifier l'évaluation...</p></i> ''',
          #      }
        noEleve=True
        errorMsg=u'''Attention : pas d\'élève!<b style="text-align:center">Attention</b>: l'évaluation a été créée <b>SANS ELEVE</b>. 
                        <p><i>Vous devrez modifier l'évaluation...</p></i> '''
    else: 
        errorMsg=''
        noEleve=False
    
    logging.debug('évaluation créée')
    #on cré les compétences à évaluer
    comps_a_eval=[]
    for n in range(int(fields['fieldNbCompetences'])):
        logging.debug('comp %s' %n)
        comp_a_eval=Competence_a_evaluer(competence_id=int(fields['fieldCompetenceId_%s'%n]),
                                         numero=int(fields['fieldPlace_%s'%n])+1,
                                         plan_evaluation=plan,
                                         items=int(fields['fieldItems_%s'%n]),
                                         detail=fields.has_key('fieldDetail_%s'%n),
                                         a_note=fields.has_key('fieldNote_%s'%n),  
                                         aide=fields.has_key('fieldAide_%s'%n),
                                         user=request.user
                                         )
        if comp_a_eval.aide and ('fieldTypeAide_%s'%n in fields) and (fields['fieldTypeAide_%s'%n]!=''): 
            comp_a_eval.type_aide_id=int(fields['fieldTypeAide_%s'%n])
        if ('fieldMode_%s'%n in fields) :
            comp_a_eval.mode=fields['fieldMode_%s'%n]
        if ('fieldOption_%s'%n in fields) :
            comp_a_eval.option=fields['fieldOption_%s'%n]
        if ('fieldType_%s'%n in fields) :
            comp_a_eval.type_eval=fields['fieldType_%s'%n]
        if ('fieldMethode_%s'%n in fields) :
            comp_a_eval.methode=fields['fieldMethode_%s'%n]
        #TODO : chaque comp peut être évaluée à un moment différent
        if ('fieldDate' in fields) and (fields['fieldDate']!=''): 
            comp_a_eval.date_evaluation=datetime.datetime.strptime(fields['fieldDate'],'%d/%m/%y')
        if ('fieldBareme_%s'%n in fields) and (fields['fieldBareme_%s'%n]!=''):
            # on peut renvoyer un texte du style'=items' 
            try: 
                comp_a_eval.bareme=Decimal(fields['fieldBareme_%s'%n])
            except:
                comp_a_eval.bareme=comp_a_eval.items
        comp_a_eval.save()
        comps_a_eval.append(comp_a_eval)
        logging.debug('----')
        #plan.competences.add(comp_a_eval)
    
        #eleves=fields['fieldEleves'].split(',')
    if not noEleve:
        logging.debug('ajout eleves')
        eleves=fields['fieldEleves']
        nb_eleves=len(eleves.split(','))
        liste_eleves=Eleve.objects.extra(where=['id in (%s)' % eleves])
        #on vérfie si tous les élèves existent bien
        if len(liste_eleves)!=nb_eleves:
            plan.delete()
            eval.delete()
            return {'success':False,'errorMessage':u'''Il y a une erreur dans la liste des élèves fournis 
                <p><i>(%s demandés, %s trouvés)</i></p>''' % (nb_eleves,len(liste_eleves))}
        #on ajoute les élèves
        nbca=0
        for eleve in liste_eleves:
            eval.eleves.add(eleve)
            nbca+=len(creer_comps_eval(eleve, eval,comps_a_eval))
    else:
        logging.debug('pas de eleve')
        nb_eleves=0
        nbca=0 
        
    plan.save()
    eval.save()
    pln='s' if nb_eleves>1 else ''
    plc='s' if len(comps_a_eval)>1 else ''
    return {'success':True, 'msg':'Mise à jour effectuée. (%(nbel)s élève%(pln)s, %(nbcomp)s compétence%(plc)s, %(nbca)s données)' % {
                        'nbel':nb_eleves,'nbcomp':len(comps_a_eval),'nbca':nbca,
                        'pln':pln ,'plc':plc} + errorMsg
            }

def maj(eval,field,value):
    #effectue la mise à jour avec conversion si besoin
    typeField=unicode(type(eval.__class__._meta.get_field(field)))
    typeField=typeField[typeField.find('django.db.models.fields')+24:-2]   
    if typeField=='CharField' or typeField=='TextField':
        eval.__setattr__(field,value)
    elif typeField=='DateField' or typeField=='DateTimeField':
        eval.__setattr__(field,datetime.datetime.strptime(value,'%Y-%m-%dT%H:%M:%S'))
    try:
        eval.save()
    except ValidationError:
        return {'success':False,'errorMessage':'Erreur de format (%s pour %s)' % (typeField,value)}
    except:
        return {'success':False,'errorMessage':'Sauvegarde impossible.'}
    return {'success':True}
    
@permission_required('application.est_prof')
@render_to_json()
def modif_evaluation(request):
    logging.debug('modif <%s>' % request.POST['action'])
    if not request.POST['action']:
        return {'success':False,'errorMessage':'Pas d\'action'}
    if request.POST['action']=='update':
        logging.debug('update')
        if ('id' not in request.POST) or ('field' not in request.POST) or ('value' not in request.POST):
            return {'success':False,'errorMessage':u'Clef nécessaire manquante.'}
        try:
            eval=Evaluation.objects.get(id=request.POST['id'])
        except:
            return {'success':False,'errorMessage':u'Evaluation inconnue'}
        if request.POST['field'] not in eval.__dict__:
            return {'success':False,'errorMessage':u'Champ inconnu.'}
        return maj(eval,request.POST['field'],request.POST['value'])
    if request.POST['action']=='delete':
        logging.debug('delete')
        if ('id' not in request.POST):
            return {'success':False,'errorMessage':u'Clef nécessaire manquante.'}
        try:
            eval=Evaluation.objects.get(id=request.POST['id'])
        except:
            return {'success':False,'errorMessage':u'Evaluation inconnue'}
        if eval.user_id<>request.user.id:
            return {'success':False,'errorMessage':u'Vous ne pouvez supprimer une évaluation que vous n\'avez pas créée.'}
        try: 
            eval.delete()            
        except:
            return {'success':False,'errorMessage':'Erreur lors de la suppression.'}
        return {'success':True}
    logging.debug('--> action non reconnue')
    return {'success':False,'errorMessage':'action inconnue.'}

@permission_required('application.est_prof')
@render_to_json()
def liste_evaluations(request):
    if (not 'action' in request.GET): return {'success':False,'errorMessage':'Pas d\'action'}
    user=request.user
    #evals=Evaluation.objects.filter(Q(date_modification__gt=DEBUT_ANNEE)| Q(date_evaluation__gt=DEBUT_ANNEE))
    #evals=Evaluation.objects.all()
    evals=Evaluation.objects.select_related('user').all()
    data=[]
    for eval in evals:
        el={}
        el['id']=eval.id
        el['nom']=eval.nom        
        el['date_modification']='%s' %eval.date_modification.isoformat()
        if (eval.date_evaluation is None) : el['date_evaluation']=''
        else : el['date_evaluation']='%s' %eval.date_evaluation.isoformat()
        el['perso']=(eval.user_id==user.id)
        el['user']=eval.user.first_name
        data.append(el)
    return {'success':True,'data':data}
    

@render_to_json()
def resultats_eval(request):
    #TODO: en bd
    tpourcentageAcquisPlus='0.95'
    tpourcentageAcquis='0.75'
    tpourcentageECplus='0.50'
    tpourcentageECmoins='0.25'
    pourcentageAcquisPlus=Decimal(tpourcentageAcquisPlus)
    pourcentageAcquis=Decimal(tpourcentageAcquis)
    pourcentageECplus=Decimal(tpourcentageECplus)
    pourcentageECmoins=Decimal(tpourcentageECmoins)
    
    if  not ('id' in request.GET): 
        return {'success':False,'errorMessage':'Aucune clef.'} #,'data':{},'columns':{},'metadata':{}
    try:
        eval=Evaluation.objects.select_related('user').get(id=request.GET['id'])
    except:
        return {'success':False,'errorMessage':'Evaluation inconnue.'}
    
    #L'évaluation est éditable si créee ar l'utilisateur en cours
    editable=(eval.user_id==request.user.id)
   
    # renvois des données + metadata
    eleves=eval.eleves.all()
    logging.debug('eleves recuperes')
    # consitution comulnset fields
    columns=[]
    columns.append({"header":"Nom","dataIndex":"nom","id":"headerid", "locked": True,"sortable":True})
    columns.append({"header":u"Prénom","dataIndex":"prenom","locked": True,"sortable":True})
    columns.append({"header":u"Note / %u" % eval.points_max,"dataIndex":"note", 
                    "locked": True,"sortable":True})
   
    fields=[]
    #fields.append({"name":"eleve_id"})
    fields.append({"name":"id"})
    fields.append({"name":"nom"})
    fields.append({"name":"prenom"})
    fields.append({"name":"note"})
    nb=0
    indexScore={}; indexItems={}; indexFaits={}; indexResultat={}; indexDetail={}
    indexComp={}; indexDonnees={}
            
    # une seule requête pour récupérer toutes les compétences
    liste_id_comps=''
    liste_comps_a_eval=eval.plan_evaluation.competence_a_evaluer_set.all().order_by('numero')
    for comp_a_eval in liste_comps_a_eval:
        liste_id_comps=liste_id_comps+'%s,' % comp_a_eval.competence_id
    liste_comps=Competence.objects.extra(where=['id in (%s)' % liste_id_comps[:-1]])
    comps={}
    for i in liste_comps:
        comps[i.id]=i
    logging.debug('noms charges')
    
    for comp_a_eval in liste_comps_a_eval:
        nb+=1
        logging.debug('competence nb %s',nb)
                                
        indexResultat[comp_a_eval.numero]="resultat_%02u_%04u"%(nb,comp_a_eval.competence_id)
        indexDonnees[comp_a_eval.numero]="donnees_%02u_%04u"%(nb,comp_a_eval.competence_id)
        indexComp[comp_a_eval.numero]=comp_a_eval.competence_id
        if (comp_a_eval.items>1): st='s'
        else: st=''
        
        header='<div data-qtip="<p>%(nom)s</p> (%(nb)u item%(st)s)">%(nom)s</div>' % {
                                    'nom':comps[comp_a_eval.competence_id].nom,
                                    'nb':comp_a_eval.items,
                                    'st':st}
        columns.append({"header":header,"dataIndex":indexResultat[comp_a_eval.numero],        
                                "xtype":'templatecolumn', 
                                "width":65,'nb_items':comp_a_eval.items,
                                "sortable":True                                             
                               })
        fields.append({"name":indexDonnees[comp_a_eval.numero]})
        fields.append({"name":indexResultat[comp_a_eval.numero],'type':'text'})
               
    resultats=Competence_evaluee.objects.filter(evaluation=eval)
    res_eleve={}
    data=[]
    logging.debug('calcul résultats')
    #TODO: optimisation possible si on fait une sortie correctement triée pâr élève
    for res in resultats:
        if res_eleve.has_key(res.eleve_id):
            res_eleve[res.eleve_id].append(res)
        else:
            res_eleve[res.eleve_id]=[res]

            
    logging.debug('Construction donnees eleve')
    note={}
    note['note_max']='%u' % eval.points_max
    for eleve in eleves:
        # si on veut que les tests dans les templates fonctionnent (<tpl if="incomplet> par ex):
        #    note['incomplet']=True
        #    note['nota']=100
        #    note['max']="trop"
        #ici if="incomplet" passe, if="bonus!=null" ne passe pas
        #on contourne avec {[values.bonus==null?truc:bidule]}
        
        #data_eleve={"eleve_id":eleve.id,"nom":eleve.nom,"prenom":eleve.prenom,"note":note}
        data_eleve={"id":eleve.id,"nom":eleve.nom,"prenom":eleve.prenom,"note":note}
        logging.debug('eleve %s ' %eleve.nom)
        for resultat_eleve in res_eleve[eleve.id]:
            logging.debug('resultat eleve: ')
            data_eleve[indexResultat[resultat_eleve.numero]]={}
            data_eleve[indexDonnees[resultat_eleve.numero]]={}    
            if (resultat_eleve.score is not None) :                
                if (resultat_eleve.methode=="Pr"):
                    if (resultat_eleve.score is not None) : 
                        field='%g' % round(resultat_eleve.score,2)
                elif (resultat_eleve.methode=='Po'):
                    if (resultat_eleve.detail and (resultat_eleve.nb_faits!=None) and (resultat_eleve.nb_faits!=0)):
                        #field='%.2f %%' % (resultat_eleve.score*Decimal('100.0')/resultat_eleve.nb_faits)
                        field='%g %%' % round((resultat_eleve.score*Decimal('100.0')/resultat_eleve.nb_faits),2)
                    else:
                        #field='%.2f %%' % (resultat_eleve.score*Decimal('100.0')/resultat_eleve.items)
                        field='%g %%' % round((resultat_eleve.score*Decimal('100.0')/resultat_eleve.items),2)
                elif (resultat_eleve.methode=="D4"):
                    if (resultat_eleve.detail and (resultat_eleve.nb_faits!=None) and (resultat_eleve.nb_faits!=0)):
                        p=resultat_eleve.score/resultat_eleve.nb_faits
                    else:
                        p=resultat_eleve.score/resultat_eleve.items
                
                    if (p>=pourcentageAcquisPlus): field="A+"
                    elif (p>=pourcentageAcquis): field='A'
                    elif (p>=pourcentageECplus): field="EC+"
                    elif (p>=pourcentageECmoins): field="EC-"
                    else: field="NA"
                else: 
                    return {'success':False,'errorMessage':'Méthode inconnue : %s' % resultat_eleve.methode}
            else:
                field=''
            data_eleve[indexDonnees[resultat_eleve.numero]]['competence_eval_id']=resultat_eleve.id
            data_eleve[indexDonnees[resultat_eleve.numero]]['field']=field
            if (resultat_eleve.score is not None) : 
                #data_eleve[indexDonnees[resultat_eleve.numero]]['score']='%.2f' % resultat_eleve.score
                data_eleve[indexDonnees[resultat_eleve.numero]]['score']='%g' % round(resultat_eleve.score,2)
                calc=field
            else :
                calc='-'
                data_eleve[indexDonnees[resultat_eleve.numero]]['score']=''
            if (resultat_eleve.nb_faits is not None): 
                #data_eleve[indexDonnees[resultat_eleve.numero]]['nb_faits']='%.2f' % resultat_eleve.nb_faits
                data_eleve[indexDonnees[resultat_eleve.numero]]['nb_faits']='%g' % round(resultat_eleve.nb_faits,2)
                #calc+='/%.2f' % resultat_eleve.nb_faits
                calc+='/%g' % round(resultat_eleve.nb_faits,2)
            else: 
                if (resultat_eleve.detail):
                    calc+='/-'                        
                data_eleve[indexDonnees[resultat_eleve.numero]]['nb_faits']=''
                
            data_eleve[indexDonnees[resultat_eleve.numero]]['detail']=resultat_eleve.detail
            data_eleve[indexDonnees[resultat_eleve.numero]]['items']=resultat_eleve.items
            data_eleve[indexDonnees[resultat_eleve.numero]]['methode']=resultat_eleve.methode
            data_eleve[indexDonnees[resultat_eleve.numero]]['mode']=resultat_eleve.mode
            data_eleve[indexDonnees[resultat_eleve.numero]]['type_eval']=resultat_eleve.type_eval
            data_eleve[indexDonnees[resultat_eleve.numero]]['option']=resultat_eleve.option
            data_eleve[indexDonnees[resultat_eleve.numero]]['a_note']=resultat_eleve.a_note
            data_eleve[indexDonnees[resultat_eleve.numero]]['aide']=resultat_eleve.aide
            if (resultat_eleve.type_aide is not None):
                data_eleve[indexDonnees[resultat_eleve.numero]]['type_aide']=resultat_eleve.type_aide_id
            else:
                data_eleve[indexDonnees[resultat_eleve.numero]]['type_aide']='-1'
            data_eleve[indexDonnees[resultat_eleve.numero]]['bareme']='%g' % round(resultat_eleve.bareme,2)
            if resultat_eleve.points_calcules is not None:
                data_eleve[indexDonnees[resultat_eleve.numero]]['points_calcules']='%g' % round(resultat_eleve.points_calcules,2)
            else:
                data_eleve[indexDonnees[resultat_eleve.numero]]['points_calcules']=''
            if resultat_eleve.points is not None:
                data_eleve[indexDonnees[resultat_eleve.numero]]['points']='%g' % round(resultat_eleve.points,2)
            else:
                data_eleve[indexDonnees[resultat_eleve.numero]]['points']=''
            data_eleve[indexDonnees[resultat_eleve.numero]]['remarques']=resultat_eleve.remarques
            if resultat_eleve.date_evaluation is not None:
                data_eleve[indexDonnees[resultat_eleve.numero]]['date_evaluation']='%s' %resultat_eleve.date_evaluation.isoformat()
            else:
                data_eleve[indexDonnees[resultat_eleve.numero]]['date_evaluation']=''
            data_eleve[indexResultat[resultat_eleve.numero]]=calc
        data.append(data_eleve)
    if 'test' in request.GET:
        return { "toutdata":{
                         "metaData": {
                                      "root":"data",
                                      #"id":"eleve_id",
                                      "id":"id",
                                      "eval_id":eval.id
                                      
                                      },
                        "columns":columns,
                        "fields":fields,
                        'data':data,
                        'success': True
                        }
            }
    else:
        return {'metaData':{'root':'data',
                            'fields':fields,
                            'columns':columns,
                            'eval':{'id':eval.id,'description':eval.description,'note':eval.a_note,
                                    'nom':eval.nom,'user':eval.user.first_name,
                                    'date_modification':eval.date_modification.isoformat(),
                                    'date_evaluation':eval.date_evaluation.isoformat()}
                            },
                'success':True,
                'data':data,
                
                }

@render_to_json()
def modif_resultats(request):
    """
    Sauvegarde des modifications effectuées sur des compétences_evaluées
    endtrée (json) -> data: [{résultat_***, donnees_****}]
    """
    data= simplejson.loads(request.raw_post_data)
    
  
    
    #si on envoie une seule donnee ce n'est pas une liste->on transforme
    if isinstance(data['data'],dict):
        data['data']=[data['data']]
        
    # on vérifie chaque competence_evaluee
    liste_comps=[]
    for ligne in data['data']:
        for comp_eval_donnees in ligne:  
            if (comp_eval_donnees.find('donnees_')==0):
                try:
                    comp_eval=Competence_evaluee.objects.get(id=ligne[comp_eval_donnees]['competence_eval_id'])
                except:
                    return {'success':False,'errorMessage':u'Compétence évaluée %s non connue.' % ligne[comp_eval_donnees]['competence_eval_id']}
                
                change=ligne[comp_eval_donnees]
                #if (change.score>change.nb_faits) or (change.score>change.items):
                #    return {'success':False,'errorMessage':u'Erreur de score.'}
                # on reçoit les réels au format float, on les veut en decimal
                if change['score']!='':
                    comp_eval.score=Decimal(str(change['score']))
                else: 
                    comp_eval.score=None
                if change['nb_faits']!='':
                    comp_eval.nb_faits=Decimal(str(change['nb_faits']))
                else:
                    comp_eval.nb_faits=None
                comp_eval.detail=change['detail']
                comp_eval.a_note=change['a_note']
                comp_eval.methode=change['methode'].capitalize()
                if change['date_evaluation']!='':
                    try:
                        comp_eval.date_evaluation=datetime.datetime.strptime(change['date_evaluation'],'%Y-%m-%dT%H:%M:%S')
                    except ValueError:
                        comp_eval.date_evaluation=datetime.datetime.strptime(change['date_evaluation'],'%Y-%m-%d')
                if change['remarques'] is not None:
                    comp_eval.remarques=change['remarques']
                comp_eval.mode=change['mode'].capitalize()
                comp_eval.type_eval=change['type_eval'].capitalize()
                comp_eval.option=change['option'].capitalize()
                if change['type_aide']=='-1':
                    comp_eval.aide=False
                    comp_eval.type_aide=None
                else:
                    comp_eval.aide=True
                    comp_eval.type_aide_id=change['type_aide']
                if change['points']!='':
                    comp_eval.points=change['points']
                else:
                    comp_eval.points=None
                if change['points_calcules']!='':
                    comp_eval.points_calcules=change['points_calcules']
                else:
                    comp_eval.points_calcules=None
                if change['bareme']!='':
                    comp_eval.bareme=change['bareme']
                else:
                    comp_eval.bareme=comp_eval.items
                # on valide le model
                try:
                    comp_eval.full_clean(exclude=['eleve','competence','evaluation','user'])
                    #comp_eval.clean()
                except ValidationError as e:                    
                    #return {'success':False,'errorMessage':e.message_dict['__all__']}                
                    return {'success':False,'errorMessage':e.message_dict}
                liste_comps.append(comp_eval)
                
   
    #construction du message de retour
    nb=0
    erreurs=[]
    for comp_eval in liste_comps:
        try:
            comp_eval.save()
            nb+=1
        except ValidationError as e:          
            #TODO: traiter et envoyer l'erreur  
            erreurs.append(comp_eval)
            nb-=1        
    if nb>1: pl='s'
    else: pl=''  
    if len(erreurs)==0:
        return {'success':True,'msg':u'%(nb)s donnée%(pl)s sauvegardée%(pl)s ' %  {'nb':nb,'pl':pl}}
    else:
        liste_erreurs_id=",".join(str(i.id) for i in erreurs)
        msg={}
        msg['Erreur lors de la sauvegarde']='''%(nb)s donnée%(pl)s sauvegardée%(pl)s<p>           
                erreurs sur %(liste)s</p>''' % {'nb':nb,'pl':pl,'liste':liste_erreurs_id}
        return {'success':False,'errorMessage':msg}
    

@permission_required('application.est_prof')
@render_to_json()
def validation_directe(request):
    if ('action' not in request.POST) or ('type' not in request.POST) or ('comps_id' not in request.POST) or ('eleve_id' not in request.POST):
        return {'success':False,'errorMessage':u'Clef nécessaire manquante.'}
    try:
        eleve=Eleve.objects.get(id=request.POST['eleve_id'])    
        
        
    except:
        return {'succes':False,'errorMessage':u'Eleve introuvable.'}
    dico_ids=simplejson.loads(request.POST['comps_id'])
    liste_id_comps=','.join(str(i) for i in dico_ids)
    try:
        comps=Competence.objects.extra(where=['id in (%s)' % liste_id_comps])
    except:
        return {'succes':False,'errorMessage':u'Une au moins des compétences est introuvable.'}
    user=User.objects.get(username=request.user)
    i=0
    for comp in comps:            
        comp_eval=Competence_evaluee(eleve=eleve,competence=comp,type_eval='D',items=1,nb_faits=1,score=1,bareme=1,statut='C',a_note=False,
                                     date_evaluation=datetime.date.today(),user=user)
        comp_eval.save()
        i+=1
    retour={'success':True}
    if i>1:
        msg=u'%i compétences sauvegardées pour %s %s' %(i,eleve.nom,eleve.prenom)
    else :
        msg=u'%i compétence sauvegardée pour %s %s' %(i,eleve.nom,eleve.prenom)
    
    if i!=len(dico_ids):
        msg+=u'<p>ATTENTION : %s sur %s !!</p>' % (i,len-dico_ids)        
        retour['errorMessage']=u'Des compétences n\'ont pas pu être sauvegardées.'
    retour['msg']=msg
    return retour



@permission_required('application.est_prof')
@render_to_json()
def resultats_eleve(request):
    if ('action' not in request.POST) or ('id_eleve' not in request.POST):
        return {'success':False,'errorMessage':u'Clef nécessaire manquante.'}
    try:
        eleve=Eleve.objects.get(id=request.POST['id_eleve'])
    except:
        return {'succes':False,'errorMessage':u'Eleve introuvable.'}
    
    if request.POST['action']=='tous':
        comps=Competence_evaluee.objects.select_related('competence','evaluation','evaluation__user').filter(eleve=eleve)            
        data=[]
        z=1
        for i in comps:            
            record={}
            record['id']=i.id
            record['competence_id']=i.competence_id
            record['competence']=i.competence.nom 
            if i.evaluation is not None:
                record['evaluation']=i.evaluation.nom
                record['perso']=(i.evaluation.user_id==request.user.id)
                record['user']=i.evaluation.user.first_name
            else:
                record['evaluation']='(noEval)'
            #record['items']='%.2f' % i.items
            record['items']='%g' % round(i.items,2)
            #if i.nb_faits is not None: record['nb_faits']='%.2f' % i.nb_faits
            if i.nb_faits is not None: record['nb_faits']='%g' % round(i.nb_faits,2)
            if i.score is not None : 
                #record['score']='%.2f' % i.score
                record['score']='%g' % round(i.score,2)
                if i.detail and (i.nb_faits):
                    #record['resultat']='%.2f' % (i.score/i.nb_faits*100)
                    record['resultat']='%g' % round((i.score/i.nb_faits*100),2)
                else:
                    #record['resultat']='%.2f' % (i.score/i.items*100)
                    record['resultat']='%g' % round((i.score/i.items*100),2)
                 
                    
            
            record['detail']=i.detail
            if i.user_id is not None:
                record['perso']=(i.user_id==request.user.id)
            
            record['date_modification']='%s' % i.date_modification.isoformat()
            if i.date_evaluation is not None: record['date_evaluation']='%s' % i.date_evaluation.isoformat() 
            #record['methode']=i.methode
            record['methode']=i.get_methode_display()
            #record['type']=i.type_eval           
            record['type']=i.get_type_eval_display()
            z+=1
            if i.score is not None: data.append(record)            
        
    else:
        evals=Competence_evaluee.objects.filter(eleve=eleve)
        lcomps=list(evals.values_list('competence',flat=True))
        comps=Competence.objects.in_bulk(lcomps)
        
            
        data=['truc']
    return {'nb':z,'data':data}

def points(eleve,eval):
    comps=eval.competence_evaluee_set.filter(eleve=eleve)
    m=Decimal(0)
    p=Decimal(0)
    for i in comps :
        if i.a_note:
            #print "%s / %s " % (i.points_calcules,i.bareme)
            if i.points_calcules is None:                
                break;
            p+=Decimal(str(i.points_calcules))
            m+=i.bareme
    print '%s: %s/%s soit %s/20' %(eleve.nom,p,m,(p*20/m) if m!=0 else '--')
    
def copie(eval,nom):
    copie=Evaluation(nom=nom,plan_evaluation=eval.plan_evaluation,
                     description='copie' if eval.description is None else  (eval.description+'(copie)'),                     
                     user=eval.user, #à changer of course
                     a_note=eval.a_note,
                     points_max=eval.points_max,
                     coefficient=eval.coefficient
                     )
    copie.save()
    # ajout des élèves
    #TODO: chercher une méthode plus rapide, un seul hit?
    print "creation eleves"
    for el in eval.eleves.all():
        copie.eleves.add(el)
    #ajout des competence_evaluee
    print "creation comps"
    for c in eval.competence_evaluee_set.all():
        print c.eleve_id,c.numero
        cp=Competence_evaluee(eleve=c.eleve,
                              competence=c.competence,
                              numero=c.numero,
                              methode=c.methode,
                              mode=c.mode,
                              type_eval=c.type_eval,
                              aide=c.aide,
                              items=c.items,
                              detail=c.detail,
                              user=c.user, #todo a changer
                              type_aide=c.type_aide,
                              a_note=c.a_note,
                              bareme=c.bareme,
                              coefficient=c.coefficient
                              )
        cp.save()
        copie.competence_evaluee_set.add(cp)

@render_to_json()
def resultats_evaluations_mg(request):
    #TODO: en bd
    tpourcentageAcquisPlus='0.95'
    tpourcentageAcquis='0.75'
    tpourcentageECplus='0.50'
    tpourcentageECmoins='0.25'
    pourcentageAcquisPlus=Decimal(tpourcentageAcquisPlus)
    pourcentageAcquis=Decimal(tpourcentageAcquis)
    pourcentageECplus=Decimal(tpourcentageECplus)
    pourcentageECmoins=Decimal(tpourcentageECmoins)  
    if ('eleve' not in request.POST): return {'success':False,'errorMessage':u'Clé manquante'}
    if 'type' in request.POST: type=request.POST['type']
    else: type='defaut'
    if 'nonfaits' in request.POST: nonfaits=is_true(request.POST['nonfaits'])
    else: nonfaits=True
    if 'tous' in request.POST: tous=is_true(request.POST['tous'])
    else: tous=False
    
    data=[]
    if ('anode' not in request.POST or request.POST['anode']==''):
        liste=None
        
        #comps=Competence.get_root_nodes()        
        comps=Graphe_competences.get_root_nodes().select_related('competence__nom')
        for comp in comps:
            el={}
            el['nom']=comp.competence.nom
            el['competence_id']=comp.id
            #el['_tree']=comp.tree_id
            el['_tree']=comp.graphe
            el['_lft']=comp.lft
            el['_rgt']=comp.rgt
            el['_level']=comp.depth
            #el['date_modification']='%s' %comp.date_modification.isoformat()
            #el['resultat']=comp.id*10/comp.lft
            el['resultat']=-1
            el['scorefils']=-1    
            el['_is_leaf']=((comp.rgt-comp.lft)==1)
            data.append(el)
    else:
        '''
        try:
            noeud=Graphe_competences.objects.get(id=request.POST['anode'])
        except:
            return {'success':False,'errorMessage':u'Compétence inconnue'}
       '''
       
        try:
            (comps,index,score,liste)=test(request.POST['eleve'],request.POST['anode'],type=type,nonfaits=nonfaits,tous=tous)
        except:
            return {'success':False,'errorMessage':u'Erreur dans la requête'}
        for comp in comps:
            el={}            
            el['nom']=comp.nom
            el['competence_id']=comp.id
            #el['_tree']=comp.tree_id
            el['_tree']=comp.graphe
            el['_lft']=comp.lft
            el['_rgt']=comp.rgt
            el['_level']=comp.depth
            if comp.date is not None:
                el['date_modification']='%s' % comp.date.isoformat()
            
            if comp.score_detail is not None:
                el['resultat']='%g' % round(comp.score_detail*100,2)
            else:
                el['resultat']='-1'
            
            if comp.scorefils is not None:
                el['scorefils']='%g' % round(comp.scorefils*100,2)
            else:
                el['scorefils']='-1'        
            el['_is_leaf']=((comp.rgt-comp.lft)==1)
            
            data.append(el)
       
            
    #if liste is not None:
    #    return {'success':True,'liste':liste}
        #return HttpResponse(simplejson.dumps({'success':True,'liste':liste}), mimetype='application/javascript')
    #else:
        #return HttpResponse(simplejson.dumps({'success':True,'data':data}), mimetype='application/javascript')
    return {'success':True,'data':data,'test':liste}

@render_to_json()
def resultats_evaluations(request):
    #TODO: en bd
    tpourcentageAcquisPlus='0.95'
    tpourcentageAcquis='0.75'
    tpourcentageECplus='0.50'
    tpourcentageECmoins='0.25'
    pourcentageAcquisPlus=Decimal(tpourcentageAcquisPlus)
    pourcentageAcquis=Decimal(tpourcentageAcquis)
    pourcentageECplus=Decimal(tpourcentageECplus)
    pourcentageECmoins=Decimal(tpourcentageECmoins)  
    
    if 'type' in request.POST: type=request.POST['type']
    else: type='defaut'
    if 'nonfaits' in request.POST: nonfaits=is_true(request.POST['nonfaits'])
    else: nonfaits=True
    if 'tous' in request.POST: tous=is_true(request.POST['tous'])
    else: tous=False
    
    data=[]
    if ('node' not in request.POST or request.POST['node']=='' or request.POST['node']=='src'):
        #comps=Competence.get_root_nodes()        
        comps=Graphe_competences.get_root_nodes().select_related('competence__nom')
        for comp in comps:
            el={}
            el['nom']=comp.competence.nom
            el['id']=comp.id
            icon='icon-'
            if comp.user_id is not None:
                el['user']=comp.user
                el['createur']=comp.createur
                if comp.user==request.user.id:
                    icon+='user'
                else:
                    icon+='group'
            
            if comp.type_lien is not None:
                el['lien']=comp.get_type_lien_display()
                icon+='_go'
            el['iconCls']=icon
                
            #el['_tree']=comp.tree_id
            #el['date_modification']='%s' %comp.date_modification.isoformat()
            #el['resultat']=comp.id*10/comp.lft
            el['resultat']=None
            el['scorefils']=None   
            el['is_leaf']=((comp.rgt-comp.lft)==1)
            data.append(el)
    else:
        if ('eleve' not in request.POST): return {'success':False,'errorMessage':u'Clé manquante'}
        '''
        try:
            noeud=Graphe_competences.objects.get(id=request.POST['anode'])
        except:
            return {'success':False,'errorMessage':u'Compétence inconnue'}
       '''
       
        try:
            (comps,index,score,data)=test(request.POST['eleve'],request.POST['node'],
                                          type=type,nonfaits=nonfaits,tous=tous,
                                          user=request.user.id)
        except:
            return {'success':False,'errorMessage':u'Erreur dans la requête'}
        
       
            
    #if liste is not None:
    #    return {'success':True,'liste':liste}
        #return HttpResponse(simplejson.dumps({'success':True,'liste':liste}), mimetype='application/javascript')
    #else:
        #return HttpResponse(simplejson.dumps({'success':True,'data':data}), mimetype='application/javascript')
    #return {'success':True,'data':data}
    return data


def test(eleve_id,comp_id,type='defaut',nonfaits=False,tous=False,user=None):
    ''' renvoie le calcul des scores (moyenne simple) pour chaque sous compétence du noeud, plus le score cumulé 
        
        eleve_id: id de l'élève
        comp_id: id de la compétence (dans le graphe)
        type: 'defaut' -> mode de calcul normal
              'total' -> prise en compte des scores/nombre d'items
              'faits' -> prise en compte des scores/nombres d'items faits
        nonfaits: si True, considère qu'une évaluation non faite vaut 0
                  sinon (défaut) ne la prend pas en compte
        tous: si True, considère qu'une évaluation d'un fils non renseignée vaut 0
              sinon (défaut) ne prend en compte que les fils évalués
        
    '''
   
    _scores={'defaut':'score_detail',
             'total':'score_total',
             'faits':'score_fait',
             'defaut_NF':'score_detail_NF',
             'total_NF':'score_total_NF',
             'faits_NF':'score_fait_NF'}
    if nonfaits: type+='_NF'
    sql='''
            SELECT g.id AS id, g.lft AS lft, g.rgt AS rgt, g.depth AS depth, g.tree_id AS tree_id, g.graphe AS graphe,
                g.type_lien as type_lien, g.user_id as user_id, u.prenom as createur,
                c.nom AS nom, 
                 MAX(IFNULL(e.date_evaluation, 
                     IFNULL((SELECT ev.date_evaluation FROM evaluations_evaluation ev
                          WHERE e.evaluation_id=ev.id),e.date_modification))) AS date, 
                 COUNT(e.id) AS nb_evals, 
                 COUNT(e.score) AS nb_evals_faits, 
                 GROUP_CONCAT(e.score/e.items) liste_scores_total, 
                 GROUP_CONCAT(CASE WHEN e.nb_faits=0 THEN 0 ELSE e.score/e.nb_faits END) AS liste_scores_fait, 
                 GROUP_CONCAT(CASE e.detail 
                         WHEN 1 THEN 
                             CASE WHEN e.nb_faits=0 
                            THEN 0 ELSE e.score/e.nb_faits 
                            END 
                        ELSE e.score/e.items END) liste_scores, 
                 SUM(IFNULL(e.score/e.items,0))/ COUNT(e.score) AS %(total)s, 
                 SUM(IFNULL(CASE WHEN e.nb_faits=0 
                                 THEN 0 ELSE e.score/e.nb_faits 
                                 END,0))/ COUNT(e.score) AS %(faits)s, 
                 SUM(CASE e.detail WHEN 1 
                         THEN IFNULL(CASE WHEN e.nb_faits=0 
                                         THEN 0 ELSE e.score/e.nb_faits END,0) 
                        ELSE IFNULL(e.score/e.items,0) END)/ COUNT(e.score) AS %(defaut)s, 
                 SUM(IFNULL(e.score/e.items,0))/ COUNT(e.id) AS %(total_NF)s, 
                 SUM(IFNULL(CASE WHEN e.nb_faits=0 THEN 0 ELSE e.score/e.nb_faits END,0))/ COUNT(e.id) AS %(faits_NF)s, 
                 SUM(CASE e.detail WHEN 1 
                         THEN IFNULL(CASE WHEN e.nb_faits=0 THEN 0 ELSE e.score/e.nb_faits END,0) 
                        ELSE IFNULL(e.score/e.items,0) END)/ COUNT(e.id) AS %(defaut_NF)s
                FROM competences_graphe_competences g
                LEFT JOIN evaluations_competence_evaluee e ON g.competence_id=e.competence_id AND e.eleve_id=%(el_id)s
                LEFT JOIN utilisateurs_prof u ON u.id=g.user_id
                INNER JOIN competences_competence c ON g.competence_id=c.id
                WHERE g.lft>=(SELECT lft FROM competences_graphe_competences WHERE id=%(comp_id)s) 
                    AND g.lft<(SELECT rgt FROM competences_graphe_competences WHERE id=%(comp_id)s) 
                    AND g.graphe=(SELECT graphe FROM competences_graphe_competences WHERE id=%(comp_id)s) 
                    
                GROUP BY g.id
                ORDER BY g.lft ASC
            ''' % {'el_id':eleve_id,'comp_id':comp_id,
                   'total':_scores['total'],
                   'faits':_scores['faits'],
                   'defaut':_scores['defaut'],
                   'total_NF':_scores['total_NF'],
                   'faits_NF':_scores['faits_NF'],
                   'defaut_NF':_scores['defaut_NF'],
                   }
    #QS=list(Competence.objects.raw(sql,[]))    
    QS=list(Graphe_competences.objects.raw(sql,[]))
    max=len(QS)
    
    def score(index,niveau):
        scorefils=None
        nb,nbevals=0,0
        newindex=index
        fini=(index>=max-1)
        encore=not fini and (QS[index+1].depth>niveau)
        #print 'index',index,'niveau',niveau,'encore',encore
        while encore:
            (newindex,newscorefils)=score(newindex+1,niveau+1)
            nb+=1
            if newscorefils is not None:
                if scorefils is None: scorefils=newscorefils
                else: scorefils+=newscorefils
                nbevals+=1
            fini=(newindex>=max-1)
            encore=not fini and (QS[newindex+1].depth>niveau)
        if scorefils is not None:
            if tous:
                QS[index].scorefils=scorefils/nb
            else:
                QS[index].scorefils=scorefils/nbevals
        else:
            QS[index].scorefils=None            
        QS[index].nbfilsevals=nbevals
        QS[index].nbfils=nb
        
        #print '---> RETOUR',index,newindex,'QS',QS[index].scorefils,QS[index].nbfilsevals,QS[index].nbfils
        #if QS[index].scores_total is None: 
        if QS[index].__getattribute__(_scores[type]) is None:
            if scorefils is None: return (newindex,None)
            else: 
                if tous:
                    return (newindex,scorefils/nb)
                else:
                    return (newindex,scorefils/nbevals)
        elif scorefils is None: return(newindex,QS[index].__getattribute__(_scores[type]))
        else: 
            if tous:
                return (newindex,((QS[index].__getattribute__(_scores[type])+scorefils/nb)/2))
            else:
                return (newindex,((QS[index].__getattribute__(_scores[type])+scorefils/nbevals)/2))
        
    index=0
    niveau=QS[index].depth
    #print max,niveau
    #max=5
    (index,score)= score(0,niveau)

    # retour en format arborescent JSON
    parent=[]
    liste=[]
    depth=QS[0].depth
    debutdepth=depth
    for i in range(0,depth): parent.append(-1)
    for rec in QS:
        
        obj={'id':rec.id,'nom':rec.nom,                     
             'children':[]}
        if rec.__getattribute__(_scores[type]) is not None:
            obj['score']= '%g' % round(rec.__getattribute__(_scores[type])*100,2)
        else:
            obj['score']=None
        if rec.scorefils is not None:
            obj['scorefils']='%g'% round(rec.scorefils*100,2)
        else:
            obj['scorefils']=None
            
        if rec.date is not None:
            obj['date_modification']='%s' % rec.date.isoformat(),
            
        icon='icon-'
        if rec.user_id is not None:
            obj['user']=rec.user_id
            obj['createur']=rec.createur
            if rec.user_id==user:
                icon+='user'
            else:
                icon+='group'
            
        if rec.type_lien is not None:
            #obj['lien']=rec.get_type_lien_display()
            obj['lien']='icon_lien'
            icon+='_go'
        else:
            obj['lien']='icon_paslien'
        if icon!='icon-': obj['iconCls']=icon
        else: obj['iconCls']='icon-sound'
        
        if rec.depth==debutdepth:
            liste.append(obj)
            parent.append(liste[0])
        elif rec.depth>=depth:
            if rec.depth>=len(parent): parent.append(-1)
            parent[rec.depth-1]['children'].append(obj)
            parent[rec.depth]=parent[rec.depth-1]['children'][len(parent[rec.depth-1]['children'])-1]
        else:
            parent[rec.depth-1]['children'].append(obj)
            parent[rec.depth]=parent[rec.depth-1]['children'][len(parent[rec.depth-1]['children'])-1]
        depth=rec.depth
    

    return(QS,index,score,liste[0]['children'])
    
    