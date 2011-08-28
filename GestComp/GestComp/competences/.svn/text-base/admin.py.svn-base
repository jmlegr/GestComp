# -*- coding: utf-8 -*-
from django.contrib import admin

from GestComp.competences.models import Competence, Type_niveau, Niveau, Competence_a_niveaux,\
    Discipline, Matiere
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
import csv


    

class CompetenceAdmin(admin.ModelAdmin):
    list_display=('chemin','nom','niveaux','aff_matieres','aff_disciplines')
    list_filter=('tree_id','disciplines','matieres')
    search_fields=('nom','description','chemin')
    actions=['sort_csv',]

   
    def sort_csv(self, request, queryset):
        '''action : créer un fichier csv à partir de la sélection'''
        response=HttpResponse(mimetype='text/csv')
        response['Content-Disposition']='attachment: filename=competences.csv'
        writer=csv.writer(response)    
        writer.writerow([unicode('Chemin').encode("utf-8"),unicode('Nom').encode("utf-8"),unicode('Description').encode("utf-8"),'niveaux'])
        comps=queryset
        for c in comps:
            try:
                cn=Competence_a_niveaux.objects.get(competence=c)
            except:
                l=''
            else:
                if cn.niveaux:
                    l=''
                    for n in cn.niveaux.all() :
                        l+=n.nom+', '
                    l=l[:-2]
                else:
                    l='(aucun niveau assigné)'        
            writer.writerow([unicode(c.chemin).encode("utf-8"),unicode(c.nom).encode("utf-8"),unicode(c.description).encode("utf-8"),\
                         unicode(l).encode("utf-8")])
        return response
    # ceci ne fonctionne pas :
    #sort_csv.short_description=unicode('Enregistrer la sélection en csv').encode("utf-8")    
    # ni ça:
    sort_csv.short_description=u'Enregistrer la sélection en csv'
    # ni ça, bien sur:
     #sort_csv.short_description='Enregistrer la sélection en csv'
    #sort_csv.short_description='Enregistrer la selection en csv'    
        
    def save_model2(self,request,obj,form):
        ''' sauvegarde du modèle en construisant l'arbre '''
        try:
            parent=Competence.objects.get(id=form.data['parent'])
        except (Competence.DoesNotExist, ValueError):
            competence=Competence.add_root(nom=obj.nom,abbrev=obj.abbrev,description=obj.description)
        else:
            competence=parent.add_child(nom=obj.nom,abbrev=obj.abbrev,description=obj.description)
        return competence
           
    def save_form(self,request,form,change):
        '''sauvegarde du formulaire des competences, avec eventuellement construction de l'arbre'''
        c=super (CompetenceAdmin,self).save_form(request,form,change)
        if not change:
                c=self.save_model2(request,c,form)
        return c
        
    class Media:
        js = ['/media_admin/admin/tinymce/jscripts/tiny_mce/tiny_mce.js', '/media_admin/admin/tinymce_setup/tinymce_setup.js',]

    
class NiveauAdmin(admin.ModelAdmin):
    list_display=('nom','degre','type',)
    list_filter=('type','degre')
    ordering=('degre',)


    

admin.site.register(Competence,CompetenceAdmin)
admin.site.register(Type_niveau)
admin.site.register(Niveau,NiveauAdmin)
admin.site.register(Discipline)
admin.site.register(Matiere)
