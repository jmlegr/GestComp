#!/usr/bin/env python
# -*- coding: utf-8 -*-
"Nested Sets de plusieurs arbres liés"
import operator
from django import VERSION as DJANGO_VERSION
from django.db import models, connection, transaction
from django.core import serializers
from django.db.models import Q

class LienInvalide(Exception):
    "raised quand la création d'un lien est invalide"
class InvalidPosition(Exception):
    "raised pour une position invalide pour add_"
    
class MissingNodeOrderBy(Exception):
    "raised"
    
class Graphe_NodeQuerySet(models.query.QuerySet):
    def delete(self, removed_ranges=None):
        """
        Custom delete method, will remove all descendant nodes to ensure a
        consistent tree (no orphans)

        :returns: ``None``
        """
        if removed_ranges is not None:
            # we already know the children, let's call the default django
            # delete method and let it handle the removal of the user's
            # foreign keys...
            super(Graphe_NodeQuerySet, self).delete()
            cursor = connection.cursor()

            # Now closing the gap (Celko's trees book, page 62)
            # We do this for every gap that was left in the tree when the nodes
            # were removed.  If many nodes were removed, we're going to update
            # the same nodes over and over again. This would be probably
            # cheaper precalculating the gapsize per intervals, or just do a
            # complete reordering of the tree (uses COUNT)...
            for graphe, drop_lft, drop_rgt in sorted(removed_ranges,
                                                      reverse=True):
                sql, params = self.model._combler_trou_sql(drop_lft, drop_rgt,
                                                            graphe)
                cursor.execute(sql, params)
        else:
            # we'll have to manually run through all the nodes that are going
            # to be deleted and remove nodes from the list if an ancestor is
            # already getting removed, since that would be redundant
            removed = {}
            for node in self.order_by('graphe', 'lft'):
                found = False
                for rid, rnode in removed.items():
                    if node.is_descendant_of(rnode):
                        found = True
                        break
                if not found:
                    removed[node.id] = node
            
            # ok, got the minimal list of nodes to remove...
            # we must also remove their descendants
            toremove = []
            ranges = []
            for id, node in removed.items():
                toremove.append(Q(lft__range=(node.lft, node.rgt)) &
                                Q(graphe=node.graphe))
                ranges.append((node.graphe, node.lft, node.rgt))
            
            if toremove:
                self.model.objects.filter(
                    reduce(operator.or_, toremove)).delete(
                    removed_ranges=ranges)
        transaction.commit_unless_managed()

class Graphe_NodeManager(models.Manager):
    """ Custom manager for nodes.
    """

    def get_query_set(self):
        "Sets the custom queryset as the default."
        return Graphe_NodeQuerySet(self.model).order_by('graphe', 'lft')
    
GRAPHE_TYPE_LIEN=(
        ('E',u'équivalence'),
        ('D',u'décomposition'),
        )

class Graphe_Node(models.Model):
    #competence=models.ForeignKey(Competence,unique=True)
    graphe=models.PositiveIntegerField(db_index=True)
    niveau=models.PositiveIntegerField(db_index=True)
    tree_id=models.PositiveIntegerField(db_index=True)
    depth=models.PositiveIntegerField(db_index=True)
    lft=models.PositiveIntegerField(db_index=True)
    rgt=models.PositiveIntegerField(db_index=True)
    type_lien=models.CharField(max_length=3,choices=GRAPHE_TYPE_LIEN,null=True)
    objects= Graphe_NodeManager()
    @classmethod
    def delete_graphe(cls,graphe):
        cls.objects.filter(graphe=graphe).delete()
        #décalage a gauche:
        cursor=connection.cursor()
        sql,params=cls._move_tree_right(graphe+1,True)
        cursor.execute(sql,params)
        transaction.commit_unless_managed()
        '''todo: oter les liens'''
      
    def delete(self):
        "Removes a node and all it's descendants."
        self.__class__.objects.filter(id=self.id).delete()
    @classmethod
    def liste(cls,graphe=None):
        if graphe==None:
            q=cls.objects.all()
        else:
            q=cls.objects.filter(graphe=graphe)
        for obj in q:
            print obj
            
    @classmethod
    def _get_serializable_model(cls):
        """
        Returns a model with a valid _meta.local_fields (serializable).

        Basically, this means the original model, not a proxied model.

        (this is a workaround for a bug in django)
        """
        if DJANGO_VERSION >= (1, 1):
            while cls._meta.proxy:
                cls = cls._meta.proxy_for_model
        return cls
    @classmethod
    def _creer_trou_sql(cls,drop_lft,drop_rgt,gap,graphe):
        "crée un trou dans l'arbre avant insertion"
        sql='UPDATE %(table)s ' \
              ' SET lft = CASE ' \
              '           WHEN lft >= %(drop_rgt)d ' \
              '           THEN lft + %(gapsize)d ' \
              '           ELSE lft END, ' \
              '     rgt = CASE ' \
              '           WHEN rgt >= %(drop_rgt)d ' \
              '           THEN rgt + %(gapsize)d ' \
              '           ELSE rgt END ' \
              ' WHERE (lft >= %(drop_rgt)d ' \
              '     OR rgt >= %(drop_rgt)d) AND '\
              '     graphe=%(graphe)d;' % {
                  'table': connection.ops.quote_name(cls._meta.db_table),
                  'gapsize': gap,
                  'drop_rgt': drop_rgt,
                  'graphe': graphe}
        return sql, []
    @classmethod
    def _combler_trou_sql(cls,drop_lft,drop_rgt,graphe):
        "crée un trou dans l'arbre avant insertion"
        sql='UPDATE %(table)s ' \
              ' SET lft = CASE ' \
              '           WHEN lft > %(drop_lft)d ' \
              '           THEN lft - %(gapsize)d ' \
              '           ELSE lft END, ' \
              '     rgt = CASE ' \
              '           WHEN rgt > %(drop_lft)d ' \
              '           THEN rgt - %(gapsize)d ' \
              '           ELSE rgt END ' \
              ' WHERE (lft > %(drop_lft)d ' \
              '     OR rgt > %(drop_lft)d) AND '\
              '     graphe=%(graphe)d;' % {
                  'table': connection.ops.quote_name(cls._meta.db_table),
                  'gapsize': drop_rgt-drop_lft+1,
                  'drop_lft': drop_lft,
                  'graphe': graphe}
        return sql, []
    
    @classmethod
    def _move_tree_right(cls, graphe,moveLeft=False):
        if moveLeft: sens=" - "
        else: sens=" + "
        sql = 'UPDATE %(table)s ' \
              ' SET graphe = graphe %(sens)s 1 ' \
              ' WHERE graphe >= %(graphe)d' % {
                  'table': connection.ops.quote_name(cls._meta.db_table),
                  'sens':sens,
                  'graphe': graphe}
        return sql, []
    
    @classmethod
    def creer_lien(cls,from_node,target_node,type_lien=None):
        ''' 
            crée un lien entre from_node et target_node ainsi que tous ses descendants
            type_lien:  'E' pour créer une équivalence entre 2 noeuds
                        'D' pour indiquer une décomposition
        '''
        if from_node.graphe==target_node.graphe:
            raise LienInvalide("Impossible de créer un lien d'un graphe sur lui même (%s)" % target_node.graphe)
        if from_node.graphe>target_node.graphe:
            raise LienInvalide("Impossible de créer un lien sur un graphe de moindre importance "\
                               "(%s > %s)" % (from_node.graphe,target_node.graphe))
        if from_node.tree_id==target_node.tree_id:
            raise LienInvalide("Impossible de créer un lien entre deux noeuds d'un même arbre (%s)" % target_node.tree_id)
        if from_node.niveau>=target_node.niveau:
            raise LienInvalide("Impossible de créer un lien sur un graphe de niveau moindre ou égal"\
                               "(%s > %s)" %(from_node.niveautarget_node.niveau))            
        gap=target_node.rgt-target_node.lft+1
        decal=from_node.rgt-target_node.lft
        depthdiff = target_node.depth - from_node.depth-1
        cursor = connection.cursor()
        
        "on crée le trou"
        sql, params= cls._creer_trou_sql(from_node.lft,from_node.rgt,gap,from_node.graphe)
        if sql :
            cursor.execute(sql,params)
            #transaction.commit_unless_managed()
         
        "copie de la partie du graphe target avec modification des lft rgt et depth"
        sql = "CREATE TEMPORARY TABLE IF NOT EXISTS tmp " \
              "SELECT * FROM  %(table)s " \
              " WHERE graphe = %(target_graphe)d AND " \
              "     lft BETWEEN %(targetlft)d AND %(targetrgt)d ;"\
               % {
                  'table': connection.ops.quote_name(cls._meta.db_table),
                  'from_graphe':from_node.graphe,
                  'from_tree': from_node.tree_id,
                  'target_graphe':target_node.graphe,
                  'target_tree': target_node.tree_id,
                  'target_niveau': target_node.niveau,
                  'decal': decal,
                  'depthdiff': depthdiff,
                  'targetlft': target_node.lft,
                  'targetrgt': target_node.rgt}
        cursor.execute(sql, [])
        
        sql=  "UPDATE tmp "\
              " SET graphe=%(from_graphe)d," \
              "     lft = lft + %(decal)d , " \
              "     rgt = rgt + %(decal)d , " \
              "     depth = depth - %(depthdiff)d ; " \
                % {
                  'table': connection.ops.quote_name(cls._meta.db_table),
                  'from_graphe':from_node.graphe,
                  'from_tree': from_node.tree_id,
                  'target_graphe':target_node.graphe,
                  'target_tree': target_node.tree_id,
                  'target_niveau': target_node.niveau,
                  'decal': decal,
                  'depthdiff': depthdiff,
                  'targetlft': target_node.lft,
                  'targetrgt': target_node.rgt}
        
        cursor.execute(sql, [])
       
        "prise en compte du type de lien, uniquement sur le noeud target"
        #TODO: vérifier la validité du type de lien
        if type_lien is not None:
            sql="UPDATE tmp "\
                "SET type_lien=\'%(type_lien)s\' "\
                "WHERE id=%(target_id)s;"\
                % {'type_lien':type_lien,
                   'target_id':target_node.id}
        cursor.execute(sql, [])
       
        "mise à jour du graphe"
        sql="Update tmp set id=0;"
        cursor.execute(sql, [])
        
        sql="INSERT INTO %(table)s"\
            "SELECT * FROM tmp;" % {'table':connection.ops.quote_name(cls._meta.db_table)}
        cursor.execute(sql, [])
        
        #"TRUNCATE  TABLE tmp;"\
        '''
        cursor.execute(sql, [])
        cursor.execute("select * from tmp",[])
        r=cursor.fetchall()
        '''
        cursor.execute("drop temporary table tmp", [])
        transaction.commit_unless_managed()
    
    def is_leaf(self):
        return (self.rgt-self.lft==1)
    
    @classmethod
    def get_tree(cls, parent=None):
        """
        :returns: A *queryset* of nodes ordered as DFS, including the parent.
                  If no parent is given, all trees are returned.
        """
        if parent is None :
            # return the entire tree
            return cls.objects.all()
            
        if parent.is_leaf():
            return cls.objects.filter(pk=parent.id)
        return cls.objects.filter(
                                      graphe=parent.graphe,
                                      lft__range=(parent.lft, parent.rgt - 1)
                                      )
        
    def get_descendants(self):
        """
        :returns: A queryset of all the node's descendants as DFS, doesn't
            include the node itself
        """
        if self.is_leaf():
            return self.__class__.objects.none()
        return self.__class__.get_tree(self).exclude(pk=self.id)

    def get_descendant_count(self):
        ":returns: the number of descendants of a node."
        return (self.rgt - self.lft - 1) / 2
        
    def get_ancestors(self):
        """
        :returns: A queryset containing the current node object's ancestors,
            starting by the root node and descending to the parent.
        """
        if self.is_root():
            return self.__class__.objects.none()
        return self.__class__.objects.filter(
            graphe=self.graphe,
            lft__lt=self.lft,
            rgt__gt=self.rgt)
    
    def get_children(self):
        ":returns: A queryset of all the node's children"
        return self.get_descendants().filter(depth=self.depth + 1)

    def get_depth(self):
        ":returns: the depth (level) of the node"
        return self.depth

    def get_root(self):
        ":returns: the root node for the current node object."
        if self.lft == 1:
            return self
        return self.__class__.objects.get(graphe=self.graphe,
                                          lft=1)
    
    @classmethod
    def get_root_nodes(cls):
        ":returns: A queryset containing the root nodes in the tree."
        return cls.objects.filter(lft=1)
        
    def is_root(self):
        ":returns: True if the node is a root node (else, returns False)"
        return self.get_root() == self
        
    def get_siblings(self):
        """
        :returns: A queryset of all the node's siblings, including the node
            itself. 
        """
        if self.lft == 1:
            return self.get_root_nodes()
        return self.get_parent(True).get_children()
    
    def get_parent(self, update=False):
        """
        :returns: the parent node of the current node object.
            Caches the result in the object itself to help in loops.
        """
        if self.is_root():
            return
        try:
            if update:
                del self._cached_parent_obj
            else:
                return self._cached_parent_obj
        except AttributeError:
            pass
        # parent = our most direct ancestor
        self._cached_parent_obj = self.get_ancestors().reverse()[0]
        return self._cached_parent_obj
    
    @classmethod
    def dump_bulk(cls, parent=None, keep_ids=True):
        "Dumps a tree branch to a python data structure."
        qset = cls._get_serializable_model().get_tree(parent)
        ret, lnk = [], {}
        for pyobj in qset:
            serobj = serializers.serialize('python', [pyobj])[0]
            # django's serializer stores the attributes in 'fields'
            fields = serobj['fields']
            depth = fields['depth']
            # this will be useless in load_bulk
            del fields['lft']
            del fields['rgt']
            del fields['depth']
            del fields['tree_id']
            if 'id' in fields:
                # this happens immediately after a load_bulk
                del fields['id']

            newobj = {'data': fields}
            if keep_ids:
                newobj['id'] = serobj['pk']

            if (not parent and depth == 1) or \
                    (parent and depth == parent.depth):
                ret.append(newobj)
            else:
                parentobj = pyobj.get_parent()
                parentser = lnk[parentobj.id]
                if 'children' not in parentser:
                    parentser['children'] = []
                parentser['children'].append(newobj)
            lnk[pyobj.id] = newobj
        return ret
    
    def is_child_of(self,node):
        return self.graphe == node.graphe and \
               self.lft > node.lft and \
               self.rgt < node.rgt and \
               self.depth==node.depth+1
    
    def is_descendant_of(self, node):
        """
        :returns: ``True`` if the node if a descendant of another node given
            as an argument, else, returns ``False``
        """
        return self.graphe == node.graphe and \
               self.lft > node.lft and \
               self.rgt < node.rgt
               
    def est_lien(self):
        """
            c'est un lien si le noeud a son parent qui n'est pas issu du meme arbre
        """
        if self.is_root():
            return False
        return self.get_parent(True).tree_id!=self.tree_id
    
    def est_dans_lien(self):
        """ 
            retourne True si le noueud fait partie d'une branche liée
        """
        if self.is_root():
            return False
        return self.get_root().tree_id!=self.tree_id

    def get_root_init(self):
        """
            retourne le noeud racine de l'arbre initial du noeud (ie non dans une branche liée)
        """    
        if self.is_root():
            return self
        return self.get_root_nodes().get(tree_id=self.tree_id)
     
    def add_child(self,**kwargs):
        """
            ajoute un enfant à droite 
        """
        cursor=connection.cursor()
        sql,params =self.__class__._creer_trou_sql(self.lft,self.rgt,2,self.graphe)
        cursor.execute(sql,params)
        noeud=self.__class__(**kwargs)
        noeud.lft=self.rgt
        noeud.rgt=self.rgt+1
        noeud.depth=self.depth+1
        noeud.graphe=self.graphe
        noeud.niveau=self.niveau
        noeud.save()
        transaction.commit_unless_managed()
        return noeud
    
    
    class Meta:
        "Abstract model."
        abstract = True    

def my_custom_sql():
    #from django.db import connection, transaction
    cursor = connection.cursor()

    # Data modifying operation - commit required
    #cursor.execute("UPDATE competences_graphe_competences SET lft = lft+100", [])
    #transaction.commit_unless_managed()

    # Data retrieval operation - no commit required
    cursor.execute("SELECT id,lft FROM competences_graphe_competences WHERE lft > %s", [10])
    rows = cursor.fetchall()
    r=[]
    
    for row in rows:
        d={}
        d['id']=row[0]
        d['lft']=row[1]
        r.append(d)
    
    #rerow=cursor.fetchone()
    return r
    