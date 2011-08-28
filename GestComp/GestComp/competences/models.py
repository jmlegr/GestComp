#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models, connection, transaction
from treebeard.ns_tree import NS_Node, NS_NodeManager
from GestComp.application.fields import AddedDateTimeField, ModifiedDateTimeField 
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from GestComp.competences.graphe import Graphe_Node


class ManyToManyField_NoSyncdb(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(ManyToManyField_NoSyncdb, self).__init__(*args, **kwargs)
        self.creates_table = False

TYPE_COMPETENCE=(
        ('FOR',u'Formelle'),    # compétence non évaluable (exemple racine de l'arbre des coméptences
        ('EVA',u'Evaluable'),   # compétence évaluable
        ('ND',u'Non définie'),
        )
MODE_CALCUL=(
        ('MAX',u'Maximum'),     # on prend le meilleur résultat
        ('MIN',u'Minimum'),     # on prend le moins bon résultat
        ('MOY',u'Moyenne'),     # on prend la moyenne des résultats
        ('PON',u'Pondérée'),    # on prend la moyenne pondérée des résultats (suivant le champs ponderation:
                                #     importance des enfants décroissante
                                #     importance décroissante suivant l'ancienneté
        )

class Mode_calcul_acquisition(models.Model):
    ''' indique le mode de calcul du niveau d'acquisition
    Pour une compétence FORMELLE :
        on fait le calcul suivant le mode acquisition_enfants sur les enfants
        
    Pour une compétence EVALUABLE :
        Si c'est une feuille (ie pas d'enfant);
            on fait le calcul suivant le mode acquisition_noeud 
            sur les compétences évaluées
        Si c'est un noeud:
            on calcule le niveau d'acquisition suivant 
            le mode acquisition_noeud
            Ce niveau devient le premier résultat pour le calcul
            suivant le mode acquisition_enfants sur les enfants,
            avec pour date la date la plus récente
    ''' 
    nom=models.CharField(max_length=30)
    acquisition_noeud=models.CharField(max_length=3,choices=MODE_CALCUL,default='MOY')
    ponderation_noeud=models.FloatField(default=1) #doit être <=1
    acquisition_enfants=models.CharField(max_length=3,choices=MODE_CALCUL,default='PON')
    ponderation_enfants=models.FloatField(default=1) #doit être <=1


class Discipline(models.Model):
    nom=models.CharField(max_length=30)
    
    def __unicode__(self):
        return u"(disc) %s" %(self.nom)
    class Meta:
        verbose_name='Discipline'

class Matiere(models.Model):
    nom=models.CharField(max_length=30)
    disciplines=models.ManyToManyField(Discipline,null=True,blank=True)
    def __unicode__(self):
        return u"(mat) %s" %(self.nom)
    class Meta:
        verbose_name='Matière'

   
#class Competence(MultiNS_Node):
class Competence(NS_Node):
    nom=models.CharField(max_length=500)
    abbrev=models.CharField(max_length=5)
    description=models.TextField(blank=True,null=True)
    chemin=models.CharField(max_length=30,blank=True)
    date_creation=AddedDateTimeField(u'Date de création',editable=False)
    date_modification=ModifiedDateTimeField(u'Dernière modification',editable=False)
    type_competence=models.CharField(max_length=3,choices=TYPE_COMPETENCE,null=True,default='ND')
    user=models.ForeignKey(User,null=True,blank=True)
    mode_calcul=models.ForeignKey(Mode_calcul_acquisition,null=True)
    matieres=models.ManyToManyField(Matiere,null=True,blank=True)
    disciplines=models.ManyToManyField(Discipline,null=True,blank=True)

    def get_desc(self,related):
        # renvoie la liste des descendants avec le select_related 
        return self.__class__.objects.filter(tree_id=self.tree_id,lft__range=(self.lft,self.rgt-1)).select_related(related)
    
    @classmethod    
    def get_root_nodes(cls,select_related=None):
        ":returns: A queryset containing the root nodes in the tree."
        #TODO : ne prends pas en compte graphe_competences_set (et tous les _set en général)
        # equivalent a get_root_nodes().select_related(...) donc a changer
        if select_related is None:
            return cls.objects.filter(lft=1)
        else:
            return cls.objects.filter(lft=1).select_related(select_related)

    @classmethod
    def get_root_nodes_infos_graphe(cls):
        ''' retourne les infos sur les noeuds plus :
                -    la liste des graphes où elle apprait, (liste_graphes)
                -    son graphe,  (graphe)
                -    son niveau  (niveau)
            TODO : tables comptence et graphe en auto
        '''
        # liste complete des champs:
        liste=cls().__dict__.keys()
        liste.remove('_state')
        champs='c.'+', c.'.join(liste)
        
        #TODO: utiliser raw(sql,params) pour éviter sql injection?
        sql='''SELECT %(champs)s,max(g.graphe) as graphe ,group_concat(g.graphe order by g.graphe) as liste_graphes, niveau
            FROM competences_competence c 
            LEFT JOIN competences_graphe_competences g on c.id=g.competence_id
            where c.lft =1            
            GROUP BY c.id
            ORDER BY c.tree_id
        ''' % {
               'champs':champs               
               }
        #raw={}
        raw=Competence.objects.raw(sql)
        #cursor = connection.cursor()
        #cursor.execute(sql,[])
        #return cursor.fetchall()
        return raw
          
    def get_children_infos_graphe(self):
        ''' retourne les infos sur la compétences plus :
                -    la liste des graphes où elle apprait, (liste_graphes)
                -    son graphe,  (graphe)
                -    son niveau  (niveau)
            TODO : tables comptence et graphe en auto
        '''
        if self.is_leaf():
            return self.__class__.objects.none()
        
        # liste complete des champs:
        liste=self.__dict__.keys()
        liste.remove('_state')
        champs='c.'+', c.'.join(liste)
        
        sql='''SELECT %(champs)s,max(g.graphe) as graphe ,group_concat(g.graphe order by g.graphe) as liste_graphes, niveau
            FROM competences_competence c 
            LEFT JOIN competences_graphe_competences g on c.id=g.competence_id
            where c.tree_id=%(tree_id)d 
            AND c.lft BETWEEN %(lft)d+1 and %(rgt)d -2
            AND c.depth=%(depth)d+1
            GROUP BY c.id
        ''' % {'tree_id':self.tree_id,
               'lft':self.lft,
               'rgt':self.rgt,
               'depth':self.depth,
               'champs':champs               
               }
        #raw={}
        raw=Competence.objects.raw(sql)
        #cursor = connection.cursor()
        #cursor.execute(sql,[])
        #return cursor.fetchall()
        return raw
        
        
    def niveaux(self):
        '''Retourne la liste des niveaux de la compétence'''
        n=self.competence_a_niveaux_set.all()
        retour=[]
        if n:            
            for niveau in n[0].niveaux.all():
                retour.append(niveau.nom)        
        return u', '.join(retour)

    
    #TODO: unifier niveaux/matieres/discplines
    def aff_disciplines(self):
        '''Retourne la liste des disciplines de la compétence'''
        disciplines=self.disciplines.all()
        retour=[]
        if disciplines:            
            for discipline in disciplines:
                retour.append(discipline.nom)        
        return u', '.join(retour)
    
        class Meta:
            verbose_name='Disciplines'
    aff_disciplines.short_description='Disciplines'
 
    def aff_matieres(self):
        '''Retourne la liste des matieres de la compétence'''
        matieres=self.matieres.all()
        retour=[]
        if matieres:            
            for matiere in matieres:
                retour.append(matiere.nom)        
        return u', '.join(retour)

        class Meta:
            verbose_name='Matières'
    aff_matieres.short_description='Matières' 
      
    def save(self):
        noeuds_chemin=self.get_ancestors()
        chemin=''
        for ancetre in noeuds_chemin:
            chemin+=ancetre.abbrev+'.'
        chemin+=self.abbrev
        self.chemin=chemin
             
        super(Competence,self).save()          
        
    def sauvegarde_simple(self):
        super(Competence,self).save()

    '''
    def __unicode__(self):
        if self.depth is not None :pre=u"+--"*(self.depth-1)
        else: pre=u"(RIEN)"
        return u"%s %s. %s" %(pre,self.abbrev,self.nom)
    '''
    def __unicode__(self):
        if self.depth is not None :pre=u"+--"*(self.depth-1)
        else: pre=u"(RIEN)"
        return u"%s %s. %s" %(pre,'abbrev',self.nom)
    def test(self):
        n=self.competence_a_niveaux_set.all()
        retour=[]
        if n:            
            for niveau in n[0].niveaux.all():
                retour.append(niveau.nom)
        retour=u', '.join(retour)
        return retour
    class Meta:
        ordering=('tree_id','lft')    

class Graphe_competences(Graphe_Node):
    competence=models.ForeignKey(Competence)
    user=models.ForeignKey(User,null=True)
    def __unicode__(self):
        pre=u"+--"*(self.depth-1)
        return u"%02u %02u. %s %s    (p%s - %s, %s)" %(self.graphe,self.niveau,pre,self.competence.nom,
                                                 self.depth,self.lft,self.rgt)
        
    @classmethod
    def init_graphe(cls,graphe,niveau,node):
        '''
            initialise un graphe en copiant un tree existant
            retourne False si un graphe de même numéro existe ou si erreur de tree
        '''
        try:
            tree=Competence.get_tree(node)
        except:
            "errreur d'arbre"
            return False
        g=cls.objects.filter(graphe=graphe).count()
        if g>0:
            "graphe existant"
            return False
        
        for competence in tree:
            
            g=cls(graphe=graphe,niveau=niveau,competence=competence,
                  tree_id=competence.tree_id, depth=competence.depth,
                  lft=competence.lft,rgt=competence.rgt)
            g.save()
        return True
    
    @classmethod
    def init_graphe_sql(cls,niveau,competence_id,graphe=None):
        '''
            initialise un graphe en copiant un tree existant  
            si le numero de graphe n'est pas donné, il sera par défaut égal
            au numéro max de graphe +1
            sinon son existence sera testée et les graphes de numéros supérieurs 
            seront éventuellement décallésvers la droite          
        '''
        niveau=int(niveau)
        competence_id=int(competence_id)
        
        #TODO: retrouver la table Competence (ou autre foreignkey) en auto
        table_comp=connection.ops.quote_name(Competence._meta.db_table)
        table=connection.ops.quote_name(cls._meta.db_table)
        if graphe is None:
            """test si la competence existe et récupère le max des graphes"""
            test=Competence.objects.extra(
                    select={'nb_graphe':'select max(graphe) from %(table)s'
                            % {'table':table}                    
                            }).filter(id=competence_id).values('id','nb_graphe')
            if test:
                graphe=test[0]['nb_graphe']+1
            else:
                return False
        else:
            """ test si le graphe et la competence existent """
            graphe=int(graphe)
            test=Competence.objects.extra(
                    select={'nb_graphe':'select count(*) from %(table)s where graphe=%(graphe)d'
                            % {'table':table, 'graphe':graphe}                    
                            }).filter(id=competence_id).values('id','nb_graphe')
            if not test:
                return False
        
        """ c'est bon, on prepare l'insertion"""
        cursor = connection.cursor()
        """la competence existe, on vérifie le graphe"""
        if test[0]['nb_graphe']>0:
            # on a un graphe existant à ce numéro. On va décaler les graphes:
            sql,params=Graphe_competences._move_tree_right(graphe)
            cursor.execute(sql,params)
                
        sql='''
                insert into %(table)s (graphe,niveau,competence_id,tree_id,depth,lft,rgt)
                select %(graphe)d,%(niveau)d,id,tree_id,depth,lft,rgt from %(table_comp)s
                where tree_id=(select tree_id from %(table_comp)s where id=%(competence_id)d)
                order by lft;
            ''' % {'table':table,
                   'table_comp':table_comp,
                   'graphe':graphe,
                   'niveau':niveau,
                   'competence_id':competence_id
                   }
        cursor.execute(sql,[])
        transaction.commit_unless_managed()
        return True
        
    @classmethod
    def get_graphe_related(cls,node=None):
        return cls.get_tree(node).select_related('competence')
    
    @classmethod
    def get_graphe(cls,id):
        # retourne le noeud du graphe associé à la compétence        
        try:
            graphe=cls.objects.filter(competence__id=id).order_by('-graphe')[0]
        except:
            return None
        return graphe
        
class Type_niveau(models.Model):
    nom=models.CharField(max_length=30)
    
    def __unicode__(self):
        return u"%s" %(self.nom)
    class Meta:
        verbose_name='type de niveau'
        verbose_name_plural='types de niveau'
        
    
class Niveau(models.Model):
    nom=models.CharField(max_length=30)
    type=models.ForeignKey(Type_niveau)
    degre=models.IntegerField(verbose_name="degré")
                
    def __unicode__(self):
        return u"(%s) %s" %(self.type.nom,self.nom)
    class Meta:
        verbose_name_plural='niveaux'
    ordering =('degre',)
    
class Competence_a_niveaux(models.Model):
    competence=models.ForeignKey(Competence,unique=True)
    niveaux=models.ManyToManyField(Niveau)
    
    def __unicode__(self):
        return u'Niveaux de (%s)%s' % (self.competence.chemin,self.competence.nom)

    class Meta:
        verbose_name='Compétence a niveau'
        verbose_name_plural='Compétence a niveaux'



