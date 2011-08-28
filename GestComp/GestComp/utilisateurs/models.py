#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import datetime
import logging



# TODO: unifier les profils utilisateurs, 
# (voir http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users )
class Prof(models.Model):
    nom=models.CharField(max_length=30)
    prenom=models.CharField(max_length=30)
    user=models.ForeignKey(User,null=True,blank=True,unique=True)
    
    def __unicode__(self):
        return "(prof)"+self.nom+' '+self.prenom
    

          
class Eleve(models.Model):
    nom=models.CharField(max_length=30)
    prenom=models.CharField(max_length=30)
    prenom2=models.CharField(max_length=30,null=True,blank=True)
    prenom3=models.CharField(max_length=30,null=True,blank=True)
    date_naissance=models.DateField('Date de naissance',null=True,blank=True)
    user= models.ForeignKey(User,null=True,blank=True,unique=True)
    actif=models.BooleanField(default=True)
    date_sortie=models.DateField('Date de sortie',null=True,blank=True)
    def __unicode__(self):
        return self.nom.capitalize() + ', '+self.prenom.capitalize()          
    
    def save(self):
        #TODO: création de user en même temps?
        if (not self.actif and (self.date_sortie==None)):
            # l'lélève sort du dispositif
            self.date_sortie=datetime.date.today()
            u=self.user
            u.is_active=False
            u.save()
            groupes=self.groupe_set.all()
            for g in groupes:
                g.eleves.remove(self)
                logging.debug('%s sorti du groupe %s',self.nom,g.nom)
            logging.debug("%s sorti du dispositif" % self.nom)
        elif (self.actif and not (self.date_sortie==None)):
            # l'élève re-rentre dans le dispositif
            self.date_sortie=None
            u=self.user
            u.is_active=True
            u.save()
            logging.debug("%s entre dans le dispositif" % self.nom)
        super(Eleve,self).save()
        logging.info(u"élève %s, %s sauvegardé" %(self.nom,self.prenom))
        
class Groupe(models.Model):
    nom=models.CharField(max_length=30,unique=True)
    description=models.TextField(null=True,blank=True)
    grp_classe=models.BooleanField(default=False)
    responsable=models.ForeignKey(Prof,related_name='responsable',null=True,blank=True)
    profs=models.ManyToManyField(Prof,related_name='profs',null=True,blank=True)
    eleves=models.ManyToManyField(Eleve,null=True,blank=True)
    public=models.BooleanField(default=False)
    user=models.ForeignKey(User,null=True,blank=True,unique=True)
    def __unicode__(self):
        if self.grp_classe:
            return '(classe)'+self.nom
        return self.nom
