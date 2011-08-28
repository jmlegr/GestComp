#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class acces_utilisateur(models.Model):
    class Meta:
        permissions = (
            ('est_prof',u'possède les droits d\'accès professeur'),
            ('est_eleve',u'possède les droits d\'accès élève'),
            ('est_admin',u'possède les droits d\'administration'),
        )