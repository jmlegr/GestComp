#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User,Group
import datetime
import logging
from settings import GROUP_ID_ELEVE

def User_Exists(user_name):
    # teste l'existence d'un utilisateur user_name
    try:
        user=User.objects.get(username=user_name)
    except User.DoesNotExist:
        return False
    return True

def supprime_accent(ligne):
        """ supprime les accents du texte source """
        accents = { 'a': [u'à', u'ã', u'á', u'â',u'ä'],
                    'e': [u'é', u'è', u'ê', u'ë'],
                    'i': [u'î', u'ï'],
                    'u': [u'ù', u'ü', u'û'],
                    'o': [u'ô', u'ö'],
                    'c': [u'ç'] }
        for (char, accented_chars) in accents.iteritems():
            for accented_char in accented_chars:
                ligne = ligne.replace(accented_char, char)
        return ligne

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
    
    @classmethod    
    def create(cls,nom,prenom,**kwargs):
        '''
        Création d'un élève et de l'utilisateur associé
        '''
        # recherche dun nom d'utilisateur non existant
        nom_utilisateur=supprime_accent(prenom[0].lower()+nom[:8].lower())
        if User_Exists(nom_utilisateur):
            cpt=1
            while User_Exists(nom_utilisateur+str(cpt)):
                cpt+=1
            nom_utilisateur+=str(cpt)
        # creation de lutilisateur (avec mot de passe idem login)
        
        utilisateur=User.objects.create_user(nom_utilisateur,'', nom_utilisateur)  
        utilisateur.last_name=nom
        utilisateur.first_name=prenom
        utilisateur.is_staff=False
        # TODO: cas aucun Group créé ou mauviase id
        utilisateur.groups.add(Group.objects.get(id=GROUP_ID_ELEVE))
        #utilisateur.set_password(utilisateur.username)
        utilisateur.save()
        #cretion de l'objet
        kwargs.update({'nom':nom,'prenom':prenom,'user':utilisateur})
        obj=cls(**kwargs)
        obj.save()   
        return obj
        
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
