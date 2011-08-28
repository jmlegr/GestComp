#!/usr/bin/env python
# -*- coding: utf-8 -*-
from GestComp.utilisateurs.models import Eleve,Prof,Groupe
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django import forms



#definition des id profs et eleves
GROUP_ID_PROF=1
GROUP_ID_ELEVE=2
def users_get_id_groupe_prof():
    return GROUP_ID_PROF

def users_get_id_groupe_eleve(): 
    return GROUP_ID_ELEVE

def is_prof(user):
    return (user.is_staff and user.is_active) or user.is_superuser

def is_eleve(user):
    return (user.is_active and not user.is_staff) or user.is_superuser

def is_admin(user):
    return user.is_superuser

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


class profAdmin(admin.ModelAdmin):
    exclude=('user',)
    list_display=('nom','prenom','user')
    
    def save_model(self,request,obj,form,change):
        '''Sauvegarde du en créant éventuellement le user lié'''
        if change:
            #Modification de l'utilisateur existant
            u=obj.user
            u.last_name=obj.nom
            u.first_name=obj.prenom
            u.save()
        else:
            # recherche dun nom d'utilisateur non existant
            nom_utilisateur=supprime_accent(obj.prenom[0].lower()+obj.nom[:8].lower())
            if User_Exists(nom_utilisateur):
                cpt=1
                while User_Exists(nom_utilisateur+str(cpt)):
                    cpt+=1
                nom_utilisateur+=str(cpt)
            # creation de lutilisateur (avec mot de passe idem login)
            utilisateur=User.objects.create_user(nom_utilisateur,'', nom_utilisateur)  
            utilisateur.last_name=obj.nom
            utilisateur.first_name=obj.prenom
            utilisateur.is_staff=True
            # TODO: cas aucun Group créé ou mauviase id
            utilisateur.groups.add(Group.objects.get(id=users_get_id_groupe_prof()))
            utilisateur.set_password(utilisateur.username)
            utilisateur.save()
            obj.user=utilisateur
        obj.save()
 
 

class eleveAdmin(admin.ModelAdmin):
 
    exclude=('user',)
    list_display=('nom','prenom','user')
  
  
    def save_model(self,request,obj,form,change):
        ''' sauvegrade de l'élève en crééant éventuellement un user'''
        if change:
            #Modification de l'utilisateur existant
            u=obj.user
            u.last_name=obj.nom
            u.first_name=obj.prenom     
            u.save()
        else:
            # recherche dun nom d'utilisateur non existant
            nom_utilisateur=supprime_accent(obj.prenom[0].lower()+obj.nom[:8].lower())
            if User_Exists(nom_utilisateur):
                cpt=1
                while User_Exists(nom_utilisateur+str(cpt)):
                    cpt+=1
                nom_utilisateur+=str(cpt)
            # creation de lutilisateur (avec mot de passe idem login)
            utilisateur=User.objects.create_user(nom_utilisateur,'', nom_utilisateur)  
            utilisateur.last_name=obj.nom
            utilisateur.first_name=obj.prenom
            utilisateur.is_staff=False
            # TODO: cas aucun Group créé ou mauviase id
            utilisateur.groups.add(Group.objects.get(id=users_get_id_groupe_eleve()))
            utilisateur.set_password(utilisateur.username)
            utilisateur.save()
            obj.user=utilisateur
        obj.save()   
    

class groupAdmin( admin.ModelAdmin): #ForeignkeyAdmin
    
    list_display=('nom','responsable')
    filter_horizontal=('eleves',)
    
    list_filter=('responsable','profs')
    list_display_links=('responsable',)
    list_editable=('nom',)
    #ajax_foreignkey_fields={'responsable':('nom','prenom')}
    radio_fields={'responsable':admin.VERTICAL}
    search_fields=['eleves__nom']
    class Media:
        js = ['/media_admin/admin/tinymce/jscripts/tiny_mce/tiny_mce.js', '/media_admin/admin/tinymce_setup/tinymce_setup.js',]


admin.site.register(Prof,profAdmin)
admin.site.register(Eleve,eleveAdmin)
admin.site.register(Groupe,groupAdmin)