#!/usr/bin/env python
# -*- coding: utf-8 -*-
from GestComp.application.render2json import render_to_json
from GestComp.competences.models import Competence, Graphe_competences,\
    Mode_calcul_acquisition
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Max
import operator
from django.contrib.auth.models import User
from GestComp.utilisateurs.models import Prof
from GestComp.evaluations.models import Competence_evaluee



def infos(id):
    #cmp=Graphe_competences.objects.get(id=id)
    
    sql='''select g.id,gg.id as id_fils,g.type_lien,g.graphe,g.tree_id,g.lft,g.rgt,g.depth,c.nom from competences_graphe_competences g
inner join (select id,graphe,tree_id,lft,rgt,depth from competences_graphe_competences 
where competence_id=%(id)s) gg
inner join competences_competence c
on g.graphe=gg.graphe
and g.rgt>gg.rgt
and g.lft<gg.lft
and c.id=g.competence_id
order by graphe desc,id_fils, lft asc

        ''' % {               
               'id':id         
               }
    raw=Graphe_competences.objects.raw(sql)
    retour=[]
    rawcount=0
    
    lien_graphe={}

    for i in raw:      
        lien={}
        if (i.depth==1):            
            #nouveau lien
            if (lien_graphe!={}):                 
                retour.append(lien_graphe)      
                lien_graphe={}      
            lien_graphe['graphe']=i.graphe            
            lien_graphe['liste']=[]
            lien={}
       
        lien['nom']=i.nom
        lien['depth']=i.depth
        lien['type_lien']=i.type_lien
        if (i.type_lien is not None):
            if (i.tree_id==16):
                lien['type_lien']=u'lié %s par' %i.type_lien
            else:
                lien['type_lien']=u'insertion %s par' %i.type_lien
        lien_graphe['liste'].append(lien)   
        
    retour.append(lien_graphe)
    nbliens=len(retour)-1
    return {'success':True,'data':{'nbliens':nbliens,'liens':retour}}
 

@render_to_json()
def infos_competence_json(request):
    if ('id' in request.POST):
        id=request.POST['id']
        try:
            cmp=Graphe_competences.objects.get(id=id)
        except:
            return {'success':False}
    else: return {'success':False}
    
    sql='''select g.id,gg.id as id_fils,g.type_lien,g.graphe,g.tree_id,g.lft,g.rgt,g.depth,c.nom,u.nom as utilisateur
     from competences_graphe_competences g
inner join (select id,graphe,tree_id,lft,rgt,depth from competences_graphe_competences 
where competence_id=%(id)s) gg
inner join competences_competence c
on g.graphe=gg.graphe
and g.rgt>gg.rgt
and g.lft<gg.lft
and c.id=g.competence_id
left join utilisateurs_prof u on g.user_id=u.user_id
order by graphe desc,id_fils, lft asc

        ''' % {               
               'id':cmp.competence_id         
               }
    raw=Graphe_competences.objects.raw(sql)
    retour=[]
    rawcount=0
    
    lien_graphe={}

    for i in raw:      
        lien={}
        if (i.depth==1):            
            #nouveau lien
            if (lien_graphe!={}):                 
                retour.append(lien_graphe)      
                lien_graphe={}      
            lien_graphe['graphe']=i.graphe            
            lien_graphe['liste']=[]
            lien={}
       
        lien['nom']=i.nom
        lien['depth']=i.depth
        lien['type_lien']=i.type_lien
        lien['utilisateur']=i.utilisateur
        if (i.type_lien is not None):
            if (i.tree_id==cmp.tree_id):
                lien['type_lien']=u'lié %s par' %i.type_lien
            else:
                lien['type_lien']=u'insertion %s par' %i.type_lien
        lien_graphe['liste'].append(lien)   
        
    retour.append(lien_graphe)
    nbliens=len(retour)-1
    return {'success':True,'data':{'nbliens':nbliens,'liens':retour}}
                        

def liste_piliers(request):
    #TODO : envois liste pilier d'un arbre + définir dans l'arbre s'il a des piliers?
    comps=Competence.objects.get(nom="segpa").get_children() | Competence.get_root_nodes()
    #préparation de la sortie en JSON
    retour={'identifier':'id',
            'label':'nom',
            'items':[]}
    for c in comps:
        item={}
        item['id']=c.id
        item['nom']='...'*(c.depth-1)+c.nom
        item['text']=c.nom
        item['chemin']=c.chemin
        item['depth']=c.depth
        item['type']='noeud'
        retour['items'].append(item)
    return retour['items']

@render_to_json()
def liste_competences_json(request):
    #TODO: gestion des erreurs
    if (not request.GET.has_key('action')): return {'success':False,'error':'Pas d\'action'}
    # demande de la liste des piliers
    if (request.GET['action']=='piliers'):        
        retour={}
        retour['success']=True        
        retour['data']=liste_piliers(request)
        retour['data'].append({'id':0,'nom':'Tous'});        
        return retour

    # demande la liste des compétences d'un pilier (toutes si pilier=0)
    if (request.GET['action']=='liste'):
        if (not request.GET.has_key('pilier')): pilier='0'
        else: pilier=request.GET['pilier']
        if (pilier=='0'): 
            # on envoit tout
            comps=list(Competence.objects.all().values('id','nom','chemin','description'))
        else :
            comp=Competence.objects.get(id=pilier)
            comps=list(comp.get_descendants().values('id','nom','chemin','description'))
        retour={
                    'success': True,
                    'data':comps }
        return retour
    return {'success':False, 'error':'mauvaise action'}

@login_required
@render_to_json()
def retour_branche(request):
    '''revoie la branche de l arbre des compétences définie par GET['node']
    si 'lazy'=false, renvoie la branche en profondeur (tous les descendants)
    '''
    
    def parcours_branche(noeud,iter_noeud):
        ''' parcourt la branche à partir de "noeud", retour json'''
        item={}
        item['id']=noeud.id
        item['text']=noeud.nom
        item['chemin']=noeud.chemin
        item['depth']=noeud.depth
        #item['leaf']=noeud.is_leaf()
        item['leaf']=False
        if not noeud.is_leaf():
            #c'est un noeud avec des fils
            item['children']=[]
            anc_noeud=noeud
            encore=True
            
            # parcours des fils            
            while encore:
                noeud=iter_noeud.next() # inutile de faire un try, "encore" nous suffit
                encore=(noeud.rgt<anc_noeud.rgt-1)
                # noeud.is_child_of(anc_noeud) fait une requête. On remplace
                # par un test direct
                #TODO: modifier la class NS
                # remarque : ici pas besoin de tester lft (parcours gauche à droite)
                if (noeud.rgt<anc_noeud.rgt) and (noeud.depth==anc_noeud.depth+1):
                    item['children'].append(parcours_branche(noeud,iter_noeud))
        return item
    
    envois_graphe=('graphe' in request.GET )
    
    if request.GET['node']=='ux':
        return []
    if request.GET['node']=='src':
        is_root=True
        if 'pos' in request.GET and request.GET['pos']=='gauche':
            est_graphe=True
            #TODO: intégrer le select_related a get_root_nodes (comme pour get_desc)
            comps=Graphe_competences.get_root_nodes().select_related('competence__nom')
            #comps=Graphe_competences.get_root_nodes(select_related='competence__nom')
        else :
            est_graphe=False
            if envois_graphe:
                #select_related ne marche pas sur les ..._set
                #comps=Competence.get_root_nodes().select_related('graphe_competences_set')                
                comps=Competence.get_root_nodes_infos_graphe()
                
            else:
                comps=Competence.get_root_nodes().order_by('tree_id')                
    else:
        is_root=False
        if 'pos' in request.GET and request.GET['pos']=='gauche':
            est_graphe=True
            comps=Graphe_competences.objects.get(id=request.GET['node']).get_children().select_related('competence__nom')
        else:
            est_graphe=False
            if envois_graphe:
                #comps=Competence.objects.get(id=request.GET['node']).get_children().select_related('graphe_competences_set')
                comps=Competence.objects.get(id=request.GET['node']).get_children_infos_graphe()
            else:
                comps=Competence.objects.get(id=request.GET['node']).get_children()
    items=[]
    lazy=True
    if request.GET.has_key('lazy'):
        lazy=request.GET['lazy']!='False'
    if not lazy:
        for c in comps:
            iter_arbre=Competence.get_tree(c).iterator()
            items.append(parcours_branche(iter_arbre.next(),iter_arbre))
    else:
        for c in comps:
            item={}
            item['id']=c.id
            item['is_root']=is_root
            
            if est_graphe:
                item['text']='(%2d) %s '%(c.graphe,c.competence.nom)
                item['nom']=c.competence.nom
                item['competence_id']=c.competence.id
                item['graphe']=c.graphe
                item['niveau']=c.niveau
                item['user']=c.user_id
            else:
                item['text']=c.nom
                item['nom']=c.nom
                item['user']=c.user_id
            #item['leaf']=c.is_leaf()
            item['leaf']=False
            item['feuille']=c.is_leaf()
            if c.is_leaf(): item['expandable']=True
            item['tree']=c.tree_id
            if envois_graphe :
                if c.graphe is not None : 
                    #item['text']='(%2d) %s' %(c.niveau,item['text'])
                    liste_graphes=c.liste_graphes.split(',')
                    if len(liste_graphes)>1:
                        #il y a des liens de créés
                        item['liens']='%s' % (len(liste_graphes)-1)
                        if request.user.has_perm('application.est_admin'):
                            if c.user_id is None:
                                item['iconCls']='icon-group_link'
                            elif c.user_id==request.user.id:
                                item['iconCls']='icon-user_suit'
                            else:
                                item['iconCls']='icon-folder_link'
                        elif c.user_id==request.user.id or c.user_id is None:
                            if c.depth==1:
                                item['iconCls']='icon-user'
                            else:
                                item['iconCls']='icon-folder_link'
                        else:
                            if c.depth==1:
                                item['iconCls']='icon-folder'
                            else:
                                item['iconCls']='icon-folder_link'
                        liste_graphes.remove(str(c.graphe))
                        liste=', '.join(liste_graphes)
                        item['qtip']='Des liens vers d\'autres graphes existent ('+liste+')'
                    else:
                        if request.user.has_perm('application.est_admin'):
                            if c.user_id is None:
                                item['iconCls']='icon-group'
                            elif c.user_id==request.user.id:
                                item['iconCls']='icon-user_suit'
                            else:
                                item['iconCls']='icon-user_green'
                        elif c.user_id==request.user.id or c.user_id is None:
                            item['iconCls']='icon-user'                            
                        else:
                            item['iconCls']='icon-folder'
                        item['qtip']='Aucun lien n\'a encore été créé'
                        item['liens']=None
                else:
                    item['iconCls']='icon-folder_error'
                    item['qtip']='Cette compétence ne fait pas partie d`un graphe'
                    item['qtipTitle']='Attention!'
                    
                item['liens_graphe']=c.liste_graphes
                item['graphe']=c.graphe      
                item['niveau']=c.niveau
            if est_graphe:                
                item['type_lien']=c.type_lien
                item['qtipTitle']='Lien:'
                if c.type_lien == 'E':
                    item['iconCls']='icon-arrow_right'
                    item['qtip']='Equivalencegfh'
                elif c.type_lien=='D':
                    item['iconCls']='icon-arrow_divide'
                    item['qtip']='Décomposition'
                else:
                    item['iconCls']='icon-text_heading_%s' % (operator.mod(c.niveau,6)+1)
                    #item['overCls']='cssGras' -> marche po
                    item['qtip']='pas de lien mais un qtip sur %s' % item['id']
                    item['qtitle']='Truc:'
            if request.GET.has_key('pos'): 
                item['pos']=request.GET['pos']
                #if item['pos']=='droite'and c.tree_id==5: item['iconCls']='icon-application_add' 
            items.append(item)
    return items
       
'''    check=True
    for c in comps:
        item={}
        item['id']=c.id
        item['text']=c.nom
        if c.is_leaf():
            item['leaf']=True
            item['href']="http://localhost:8080"
            item['icon']="/smedia/js/extjs/examples/tree/album.gif"
        else:
            item['checked']=check
            check=not check
            if (check) : item['cls']='ct'
        items.append(item)'''
        
def ite(e):
    if e.is_leaf(): return e.nom    
    l=[]
    ch=e.get_children()    
    for c in ch:
        l.append(ite(c))
    return l

def desc(e,related):
    if related:
        return e.__class__.objects.filter(tree_id=e.tree_id,lft__range=(e.lft,e.rgt-1)).select_related(related)
    else:
        return e.__class__.objects.filter(tree_id=e.tree_id,lft__range=(e.lft,e.rgt-1))
@render_to_json()
def test(request):
    c=Competence.objects.get(id=request.POST['competence'])
    #d=c.get_descendants()
    #a=Competence.objects.select_related(depth=1).extra(where=['id in (%s)' % ','.join(str(i.id) for i in d)])
    #a=desc(c,'user')
    a=c.get_desc('user')
    l=[]
    for i in a:
        if i.user is not None:
            l.append({'id':i.id,'user':i.user.username})
        else:
            l.append({'id':i.id,'user':''})
    return l

@render_to_json()
@permission_required('application.est_prof')
def modif_liens(request):
    try:
        cible=Graphe_competences.objects.get(id=request.POST['cible'])
    except:
        return {'success':False,'msg':u'Compétence liée inexistante'}
    cibles=Graphe_competences.objects.filter(competence__id=cible.competence_id,graphe__lte=cible.graphe)
    #on charge le queryset et on calcule le nombre de cibles
    nb_cibles=len(cibles)   
    #origine=Graphe_competences.objects.get(competence=request.POST['origine_id'],graphe=request.POST['origine_graphe'])
    origines=Graphe_competences.objects.filter(competence=request.POST['origine_id'],graphe__lte=request.POST['origine_graphe'])
    
    #recherche si des liens existent déjà
    lien=False
    for c in cibles:
        for o in origines:
            if o.is_child_of(c):
                lien=True
                break
    if lien:
        return {'success':False,'msg':u'Lien entre compétence %s et %s déjà existant' %(cible.competence_id,request.POST['origine_id'])}
    orig_temp=origines.filter(graphe=request.POST['origine_graphe'])
    if len(orig_temp)==0:
        return {'success':False,'msg':u'Compétence inexistante'}
    else: 
        origine=orig_temp[0]
    if request.POST['type']=='append':
        type_lien='E'
    else:
        type_lien='D'
    nb=0
    for cible in cibles:
        nb+=1
        # on prépare les liens avec un lien temporaire pour les retrouver
        Graphe_competences.creer_lien(cible,origine, 'TMP')
    # on met à jour les liens en rajoutant l'utilisateur
    Graphe_competences.objects.filter(type_lien='TMP').update(user=request.user,type_lien=type_lien)
    return {'success':(nb==nb_cibles),'msg':u'%s liens créés sur %s' % (nb,nb_cibles)}

@render_to_json()
@permission_required('application.est_prof')
def supprime_liens(request):
    """
        suppression du lien id et de tous les liens de même forme
        (ie lien entre competence a et b) et meme utilisateur
    """
    cible=Graphe_competences.objects.get(id=request.POST['id'])
    cible_competence_id=cible.competence_id
    type_lien=cible.type_lien
    cibles=Graphe_competences.objects.filter(competence__id=cible.get_parent().competence_id)
    nb=0
    s=''
    toremove=[]
    for parent in cibles:
        if request.user.has_perm('application.est_admin'):
            fils=parent.get_children().filter(user=cible.user,type_lien=type_lien)
        else:
            fils=parent.get_children().filter(user=request.user,type_lien=type_lien)
        for f in fils:
            if f.competence_id==cible_competence_id:
                #effacement de f
                s+='%s ' %(f.id)
                toremove.append(f)
                nb+=1
    cpt=0
    liste_id=[]
    for i in toremove:
        liste_id.append(i.id)        
        i.delete()
        cpt+=1
    return {'success':True,'msg':'%s liens supprimés (%s)' %( nb,s),'liste':liste_id}
      
@render_to_json()
@login_required()
def initialise_graphe(request):
    if not request.user.has_perm('application.est_admin'):
        return {'success':False,'msg':'Droits insuffisants'}
    if 'graphe' in request.POST and request.POST['graphe']!='':
        ok=Graphe_competences.init_graphe_sql(graphe=request.POST['graphe'],
                                              niveau=request.POST['niveau'], 
                                              competence_id=request.POST['id'])
    else:
        ok=Graphe_competences.init_graphe_sql(niveau=request.POST['niveau'], 
                                              competence_id=request.POST['id'])
    if ok:
        msg=u'Graphe initialisé'
    else:
        msg=u'Erreur d\'initialisation du graphe'
    return {'success':ok,'msg':msg}


@render_to_json()
@permission_required('application.est_admin')
def supprime_graphe(request):
    if 'id' in request.POST:
        test=Graphe_competences.objects.filter(competence__id=request.POST['id']).aggregate(graphe=Max('graphe'))
        graphe=test['graphe']
        if graphe is not None:
            Graphe_competences.delete_graphe(graphe)
            return {'success':True,'msg':u'Graphe N° %s supprimé' % graphe}
        else:
            return {'success':False,'msg':u'Pas de graphe lié à la compétence n° %s' % request.POST['id']}
    return {'success':False,'msg':'Clé manquante'}

def init_test():
    Graphe_competences.delete_graphe(0)
    Graphe_competences.delete_graphe(1)
    Graphe_competences.delete_graphe(2)
    Graphe_competences.delete_graphe(3)
    Graphe_competences.init_graphe_sql(niveau=0, competence_id=917, graphe=0)
    Graphe_competences.init_graphe_sql(niveau=1, competence_id=927, graphe=1)
    Graphe_competences.init_graphe_sql(niveau=2, competence_id=941, graphe=2)
    Graphe_competences.init_graphe_sql(niveau=2, competence_id=949, graphe=3)
    
@render_to_json()
def renommer_competence(request):
    if not('id' in request.POST and 'newName' in request.POST and 'oldValue' in request.POST):
        return {'success':False,'msg':u'Clés manquantes.'}
    oldName=request.POST['oldValue']
    newName=request.POST['newName']
    id=request.POST['id']
    try:
        comp=Competence.objects.get(id=id)
    except:
        return {'success':False,'msg':u'Compétence %s (%s) inexistante' % (oldName,id)}
    if comp.user!=request.user and not request.user.has_perm('application.est_admin') and comp.user!=None:
        return {'success':False,'msg':u'Vous n\'avez pas les permissions sur cette compétence.'}
    comp.nom=newName
    comp.save()
    return {'success':True,'msg':u'Compétence %s renommée en %s' % (oldName,newName)}

@render_to_json()
@permission_required('application.est_prof')
def ajout_competence(request):
    POST=request.POST
    if not ('id_parent' in POST and 'tree_parent' in POST and 'graphe_parent' in POST and 'newName' in POST):
        return {'success':False,'msg':u'Clés manquantes.'}
    id=POST['id_parent']
    tree=POST['tree_parent']
    graphe=POST['graphe_parent']
    newName=POST['newName']
    if id=='src' and request.user.has_perm('application.is_admin'):
        # on rajoute une racine
        comp_ajout=Competence.add_root(nom=newName,user_id=request.user.id)
        return {'success':True,'id':comp_ajout.id,'liste':[]}
        
    try:
        comp=Competence.objects.get(id=id)
    except:
        return {'success':False,'msg':u'Compétence %s (%s) inexistante' % (newName,id)}
    if (comp.user==None) or (comp.user==request.user) or request.user.has_perm('application.is_admin'):
        #user=comp.user
        user=request.user
        comp_ajout=comp.add_child(nom=newName,user=user)
        #mise à jour des graphes
        cibles=Graphe_competences.objects.filter(competence__id=id)
        liste=[]
        for comp in cibles:
            c=comp.add_child(competence_id=comp_ajout.id,tree_id=tree,user=user)
            liste.append(comp.id)
        return {'success':True,'id':comp_ajout.id,'liste':liste}
    return {'success':False,'msg':u'Vous n\'avez pas les permissions sur cette compétence.'}

@render_to_json()
def supprime_competence(request):
    if not('id' in request.POST):
        return {'success':False,'msg':u'Clés manquantes.'}
    try:
        comp=Competence.objects.get(id=request.POST['id'])
    except:
        return {'success':False,'msg':u'Compétence (%s) inexistante' % request.POST['id']}
    if comp.user!=request.user and not request.user.has_perm('application.est_admin') and comp.user!=None:
        return {'success':False,'msg':u'Vous n\'avez pas les permissions sur cette compétence.'}
    nom=comp.nom
    comps=Competence.objects.filter(id=request.POST['id'])|comp.get_descendants()
    cibles=Graphe_competences.objects.filter(competence__id=request.POST['id'])
    comps_eval=Competence_evaluee.objects.filter(competence=request.POST['id'])
    #print len(comps),len(comps_eval),len(cibles),len(comps)+len(comps_eval)+len(cibles)
    l=len(cibles)
    liste=[]
    for c in cibles:
        liste.append(c.id)
        #print 'delete ',type(c),c.id
        #c.delete()
    #comp.delete()
    comps_eval.delete()
    cibles.delete()
    comps.delete()
    return {'success':True,'msg':u'Compétence %s (%s) [et %s liens] supprimée' % (nom,request.POST['id'],l),'liste':liste}

@render_to_json()
def change_user(request):
    '''
        change l'utilisateur assoié à une compétence et ses sous-compétences
        note : si mis à 'aucun' (NULL) les utilisateurs ont libre accès (sauf suppression)
            (utile pour donner un accès temporaire pour modfier les liens/arbres)
        sinon seul le propriétaire ou l'administrateur peut agir, 
        y compris pour la création de liens
        TODO : créer une procédure pour mettre à jour les liens lors du changement d'utilisateur
        (recherche des cibles de même compétence et m^utilisateurs, maj du user sur le nouvel utilisateur)
        hmmm a voir.... 
    ''' 
    admin=request.user.has_perm('application.est_admin')
    if not admin:
        return {'success':False,'msg':u'Vous n\'avez pas les permissions nécessaires.'}
    if not('id' in request.POST and 'prof' in request.POST):
        return {'success':False,'msg':u'Clés manquantes.'}
    try:
        comp=Competence.objects.get(id=request.POST['id'])        
    except:
        return {'success':False,'msg':u'Compétence (%s) inexistante' % request.POST['id']}
    user_id=request.POST['prof']
    if user_id=='-':
        user=None
        user_name='Aucun'
    elif user_id=='admin':
        user=request.user
        user_name='Administrateur'
    else:
        try:
            user=Prof.objects.get(id=user_id).user
            user_name=user.first_name
        except:
            return {'success':False,'msg':u'Utilisateur (%s) inexistant' % user_id}
    comp.user=user
    comp.save()
    nbcomps=comp.get_descendants().update(user=user)
    #maj des liens A TESTER
    liste_id=[comp.id]+list(comp.get_descendants().values_list('id',flat=True))
    cible=Graphe_competences.get_graphe(comp.id)
    if (cible is not None):
        cibles=Graphe_competences.objects.filter(type_lien__isnull=False,graphe__lt=cible.graphe).extra(where=['competence_id in %s'],params=[liste_id])
        nbliens=cibles.update(user=user)
    else:
        nbliens=0
    nom=comp.nom
    return {'success':True,'msg':u'Compétence %s et ses %s descendants ont pour nouvel utilisateur %s ( %s liens)'
            % (nom,nbcomps,user_name,nbliens)}

import csv
def import_competence(file,skip_first_line=True):
    
    
    def nonvide(liste):
        index=0
        longueur=len(liste)
        if longueur==0:
            return -1
        while liste[index]=='':
            index+=1
            if index>=longueur:
                return -1
        return index
    
    def parcours(noeud,next,reader,max,titre):
        item={}
        i_noeud=nonvide(noeud)
        #item['data']={'nom':u'%s' % unicode(noeud[i_noeud],'utf-8')[:100]}
        #TODO: récupérer la taille max du chmps nom (ici 500)
        item['data']={'nom':u'%s' % unicode(noeud[i_noeud],'utf-8')[:500]}
        if len(item['data']['nom'])>max:
            max=len(item['data']['nom'])
            titre=item['data']['nom']
        item['children']=[]
        while nonvide(next)==i_noeud+1:
            try:
                suivant=reader.next()
            except StopIteration:
                suivant=[]
            child,next,max,titre=parcours(next,suivant,reader,max,titre)
            item['children'].append(child)
        return (item,next,max,titre)
        
        
    max=0
    titre=''    
    with open(file,'rb') as f:
        reader=csv.reader(f)
        if skip_first_line:
            try:
                reader.next()
            except StopIteration:
                return []
        try: 
            noeud=reader.next()
        except StopIteration:
            return []
        retour=[]
        try:
            next=reader.next()
        except StopIteration:
            next=[]
        encore=True
        while encore:
            (item,noeud,max,titre)=parcours(noeud,next,reader,max,titre)
            retour.append(item)
            if len(noeud)==0:
                encore=False
            else:
                try:
                    next=reader.next()
                except StopIteration:
                    next=[]
        #print max,titre                
        return retour
    
    
    
    