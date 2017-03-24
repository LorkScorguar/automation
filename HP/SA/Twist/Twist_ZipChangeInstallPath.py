"""
Script permettant de modifier le chemin d'installation d'un zip
Il prend en argument le nom du zip ainsi que le nouveau chemin
ex: 'monZIP /tmp/install'
"""

#!/opt/opsware/bin/python

import sys
sys.path.append("/opt/opsware/pylibs2")
from pytwist import *

if len(sys.argv) < 3:
        print 'You must specify a ZIP name AND an installation path'
        sys.exit(1)
else:
        arg1=sys.argv[1]
        arg2=sys.argv[2]


zipName=arg1
installPath=arg2
returnCode=0
result=""
ref=com.opsware.pkg.ZIPRef()

try:
        found=False
        ts = twistserver.TwistServer()
        zipService = ts.pkg.ZIPService

        filtreZip=com.opsware.search.Filter()
        zipRefs=zipService.findZIPRefs(filtreZip)
        for zipRef in zipRefs:
                if zipName == zipService.getZIPVO(zipRef).getName():
                        ref=zipRef
                        found=True
        if not found:
                result="Impossible de trouver un zip avec ce nom"
        else:
                zipVO=zipService.getZIPVO(ref)

                zipVO.setInstallPath(installPath)#on affecte le nouveau nom
                zipService.update(zipRef,zipVO,1,1)#on update notre zip
                result="action effectuee"
except:
        returnCode=1
        result="impossible d'effectuer l'action"
print(result)
sys.exit(returnCode)
