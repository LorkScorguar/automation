#!/opt/opsware/bin/python2.7
# -*- coding: utf-8 -*-

"""
Script permettant de recuperer l'id d'un objet HPSA.
Il prend en argument le chemin complet vers le fichier incluant le nom de ce dernier.
ex: 'Content/Configurations/crontab.tpl'
"""

import sys
sys.path.append("/opt/opsware/pylibs27")
from pytwist import *
import re

path=""
result=""
codeRetour=0

if len(sys.argv) < 2:
        print 'You must specify a folder path'
        sys.exit(1)
else:
        arg=sys.argv[1]

ts = twistserver.TwistServer()
folderService = ts.folder.FolderService #on charge le service de gestion des repertoires
try:
        p=arg.split("/")
        file=p.pop(len(p)-1)
        path=p
        folderRef=folderService.getFolderRef(path) #on recupere la reference du repertoire voulu
        childs=folderService.getChildren(folderRef) #on recupere la liste des enfants du repertoire
        for child in childs:
                f=str(child).split(' (')
                if re.match(f[0],file): #si le fils a le meme nom que celui passe en argument alors on retourne son ID
                        temp=str(child).split('Ref:')
                        result=temp[1][:-1]
        if result=="":
                result="Can't find any object which name is "+file
                codeRetour=1
except:
        result="Object not found"
        codeRetour=1
print result
sys.exit(codeRetour)
