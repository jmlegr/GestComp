#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 
 *  $Revision$
 * Dernière modification $Date$
''' 

from django.db import models
from GestComp.competences.models import Competence
from GestComp.utilisateurs.models import Prof, Groupe, Eleve
from django.contrib.auth.models import User
from GestComp.ressources.fields import AddedDateTimeField, ModifiedDateTimeField

TYPE_EVALUATION=(
        ('E',u'écrite'),
        ('O',u'orale'),
        ('D',u'directe'),
        ('M',u'maison'),
        ('A',u'autre'),         
        )
MODE_EVALUATION=(
        ('E',u'enseignant'),
        ('A',u'auto-évaluation'),
        ('P',u'pair'),
        ('I',u'informatique'),
         )

STATUT_COMP_EVAL=(
        ('NC',u'Non corrigé'),
        ('C',u'Corrigé'),
        ('ABS',u'Absent'),
        ('NF',u'Non Fait'),
        ('F',u'Fait'),
        ('B',u'Bonus'),
        ('O',u'Option'),
        ('ONF',u'Option Non faite'),
)

OPTION_COMP_EVAL=(
        ('-',u'Obligatoire'),
        ('O',u'Optionnel'),
        ('B',u'Bonus')
                  )

METHODE_EVALUATION=(
        ('Pr',u'Proportionnel'),
        ('Po',u'Pourcentage'),
        ('D4',u'Direct 4'),
        )  

STATUT_EVALUATION=(
        ('EA',u'En attente'),
        ('EC',u'En cours'),
        ('E',u'Effectuée'),
        ('CEC',u'Correction en cours'),
        ('C',u'Complète')
        )

class Competence_aide(models.Model):
    nom=models.CharField(max_length=30)
    description=models.TextField(blank=True,null=True)
    user=models.ForeignKey(User,null=True,blank=True)
    def __unicode__(self):
        return u'%s' % self.nom
 
class Plan_evaluation(models.Model):
    ''' un ensemble de compétences à évaluer liées à un ou plusierus groupe, créé par un prof'''
    nom=models.CharField(max_length=30)
    description=models.TextField(blank=True, null=True)
    competences=models.ManyToManyField(Competence,through='Competence_a_evaluer',
                                       verbose_name=u'compétences à évaluer')    
    prof=models.ForeignKey(Prof, verbose_name=u'Créateur',blank=True, null=True)
    public=models.BooleanField(default=True,help_text=u'Si public, le plan est visible/utilisable par tous.')
    #defauts
    methode=models.CharField(max_length=3,choices=METHODE_EVALUATION,null=True,default='Pr')
    items=models.IntegerField(u"nombre d'items",default=5)
    detail=models.BooleanField(default=False)
    statut=models.CharField(max_length=3,choices=STATUT_COMP_EVAL,null=True,default='NC')
    mode=models.CharField(max_length=3,choices=MODE_EVALUATION,null=True,default='E')
    type_eval=models.CharField(u"type d'évalaluation",max_length=3,choices=TYPE_EVALUATION,null=True,default='E')
    aide=models.BooleanField(default=False)
    type_aide=models.ForeignKey(Competence_aide,verbose_name=u"type d'aide",null=True,blank=True)
    user=models.ForeignKey(User,null=True,blank=True)
    date_creation=AddedDateTimeField(u'Date de création',editable=False)
    date_modification=ModifiedDateTimeField(u'Dernière modification',editable=False)
    a_note=models.BooleanField(u'noté',default=True)

    def __unicode__(self):
        retour=u'%s' % self.nom
        if self.prof:
            retour+=u' de %s.%s' % (self.prof.prenom[0],self.prof.nom[0:2])
        return retour
    
    def delete(self):
        """supprime la cascade sur evaluation"""
        self.evaluation_set.clear()
        super(Plan_evaluation,self).delete()
        
    
    class Meta:
        verbose_name=u"Plan d'évaluation"
        verbose_name_plural=u"Plans d'évaluation"
Plan_evaluation.short_description=u"Plan d'évaluation"       

class Competence_a_evaluer(models.Model):
    # une compétence liée à un modèle (pourcentage, directe..) avec un nombre d items
    # eventuellement detaillée (précision du nombre items faits)
    #grappelli online reordering
    order=models.PositiveIntegerField(blank=True,null=True)
    #numéro d'ordre dans le plan
    numero=models.IntegerField(default=0)
    competence=models.ForeignKey(Competence,null=True,blank=True)
    plan_evaluation=models.ForeignKey(Plan_evaluation,null=True)
    methode=models.CharField(max_length=3,choices=METHODE_EVALUATION,null=True,default='Pr')
    items=models.IntegerField(default=5)
    detail=models.BooleanField(default=False)
    statut=models.CharField(max_length=3,choices=STATUT_COMP_EVAL,null=True,default='NC')
    mode=models.CharField(max_length=3,choices=MODE_EVALUATION,null=True,default='E')
    type_eval=models.CharField(max_length=3,choices=TYPE_EVALUATION,null=True,default='E')
    aide=models.BooleanField(default=False)
    type_aide=models.ForeignKey(Competence_aide,verbose_name=u"type d'aide",null=True,blank=True)
    date_evaluation=models.DateField(blank=True,null=True)
    user=models.ForeignKey(User,null=True,blank=True)
    date_creation=AddedDateTimeField(u'Date de création',editable=False)
    date_modification=ModifiedDateTimeField(u'Dernière modification',editable=False)
    a_note=models.BooleanField(u'noté',default=True)
    bareme=models.DecimalField(u'barême',max_digits=5,decimal_places=2,null=True,blank=True)
    
    option=models.CharField(max_length=3,choices=OPTION_COMP_EVAL,blank=True,null=True,default='-')
    def __unicode__(self):
        if self.detail:
            det=u" détaillé)"
        else:
            det=u")"
        try:
            chemin=u'%s' % self.competence.chemin
        except:
            chemin=u'?'
        return u'%s(%s, %s items%s' % (chemin,self.methode,str(self.items),det)
    class Meta:
        verbose_name=u"Compétence à évaluer"
        verbose_name_plural=u"Compétences à évaluer"
        ordering=['order',]
Competence_a_evaluer.short_description=u"Compétence à évaluer"
   
class Evaluation(models.Model):    
    nom=models.CharField(max_length=30)
    plan_evaluation=models.ForeignKey(Plan_evaluation,verbose_name=u"plan d'évaluation",null=True)
    description=models.TextField(blank=True,null=True)
    remarques=models.TextField(blank=True,null=True)
    profs=models.ManyToManyField(Prof,verbose_name=u"Enseignants concernés",blank=True,null=True) 
    groupes=models.ManyToManyField(Groupe,blank=True,null=True)
    eleves=models.ManyToManyField(Eleve,verbose_name=u"Elèves",blank=True)
    date_evaluation=models.DateField(blank=True,null=True)
    user=models.ForeignKey(User,null=True,blank=True)
    date_creation=AddedDateTimeField(u'Date de création',editable=False)
    date_modification=ModifiedDateTimeField(u'Dernière modification',editable=False)
    fait=models.BooleanField(default=False)
    statut=models.CharField(max_length=3,choices=STATUT_EVALUATION,null=True,default='EA')
    ''' a voir, ou pour prise en compte de lanote? les competence_a_evaluer ont deja les items
    a_note, bareme'''
    a_note=models.BooleanField(u'noté',default=True)
    points_max=models.DecimalField(u'sur',max_digits=5,decimal_places=2,blank=True,null=True)
    coefficient=models.DecimalField(max_digits=5,decimal_places=2,default=1)
    aide=models.BooleanField(default=False)
    type_aide=models.ForeignKey(Competence_aide,verbose_name=u"type d'aide",null=True,blank=True)
    #TODO: creation des competence_evaluee sur add(eleve) ou add(competence)
    
    def __unicode__(self):
        return u'(Eval) %s' %self.nom
    class Meta:
        verbose_name=u"évaluation"
        verbose_name_plural=u"évaluation"

#TODO : suppression propore pour élèves, groupes, compétences (avec suppression des comps_evaluee


class Competence_evaluee(models.Model):
    eleve=models.ForeignKey(Eleve)
    competence=models.ForeignKey(Competence)
    evaluation=models.ForeignKey(Evaluation,null=True)
    numero=models.IntegerField(default=0)
    methode=models.CharField(max_length=3,choices=METHODE_EVALUATION,null=True,default='Pr')
    mode=models.CharField(max_length=3,choices=MODE_EVALUATION,null=True,default='E')
    type_eval=models.CharField(max_length=3,choices=TYPE_EVALUATION,null=True,default='E')
    aide=models.BooleanField(default=False)
    items=models.IntegerField(null=True)
    detail=models.BooleanField(default=False)
    user=models.ForeignKey(User,null=True,blank=True)
    date_evaluation=models.DateField(blank=True,null=True)
    date_creation=AddedDateTimeField(u'Date de création',editable=False)
    date_modification=ModifiedDateTimeField(u'Dernière modification',editable=False)
    nb_faits=models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    score=models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    statut=models.CharField(max_length=3,choices=STATUT_COMP_EVAL,null=True)
    aide=models.BooleanField(default=False)
    type_aide=models.ForeignKey(Competence_aide,null=True,blank=True)
    a_note=models.BooleanField(u'noté',default=True)
    bareme=models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    points=models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    points_calcules=models.FloatField(blank=True,null=True)
    coefficient=models.DecimalField(max_digits=5,decimal_places=2,default=1)
    resultat=models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    option=models.CharField(max_length=3,choices=OPTION_COMP_EVAL,blank=True,null=True,default='-')
    remarques=models.TextField(blank=True,null=True)

    def __unicode__(self):
        return u'%s pour %s' %(self.competence.chemin,self.eleve.nom)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.nb_faits>self.items:
            raise ValidationError({'nb_faits':u'Le nombre d\'items faits ne peut être supérieur au nombre d\'items.('+self.eleve.nom+','+self.competence.nom+', col.%s)' % self.numero})
        if (self.nb_faits is not None) and (self.score>self.nb_faits): 
            raise ValidationError({'score':u'Un score ne peut être supérieur au nombre d\'items faits.('+self.eleve.nom+','+self.competence.nom+', col.%s)' % self.numero})
        if self.score>self.items:
            raise ValidationError({'score':u'Un score ne peut être supérieur au nombre d\'items.('+self.eleve.nom+','+self.competence.nom+', col.%s)' % self.numero})
        
        
    def save(self):
        if self.score is not None:
            if self.detail:
                if self.nb_faits is None: self.nb_faits=self.items
                if self.nb_faits<>0:
                    self.points_calcules=(self.score/self.nb_faits)*self.bareme
                else:
                    self.points_calcules=0
            else:
                self.points_calcules=(self.score/self.items)*self.bareme
        super(Competence_evaluee,self).save()

    class Meta:
        verbose_name=u"Compétence évaluée"
        verbose_name_plural=u"compétences évaluées"

