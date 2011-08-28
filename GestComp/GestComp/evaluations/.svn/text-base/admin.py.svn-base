# -*- coding: utf-8 -*-
from django.contrib import admin
from GestComp.evaluations.models import Competence_evaluee

class CompetenceAdmin(admin.ModelAdmin):
    list_display=('chemin','nom','niveaux','aff_matieres','aff_disciplines')
    list_filter=('tree_id','disciplines','matieres')
    search_fields=('nom','description','chemin')
    
admin.site.register(Competence_evaluee)
