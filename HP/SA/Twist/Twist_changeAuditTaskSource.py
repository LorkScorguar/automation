"""
Script permettant de remplacer la source d'un audit
Il prend en argument le nom de l'audit a modifier ainsi que l'id du snapshot Result source
ex: 'TestPourHPOO 10'
"""

#!/opt/opsware/bin/python

import sys
sys.path.append("/opt/opsware/pylibs2")
from pytwist import *

if len(sys.argv) < 3:
        print 'You must specify an audit name AND a snapshot result source id'
        sys.exit(1)
else:
        arg1=sys.argv[1]
        arg2=sys.argv[2]


auditName=arg1
sourceID=arg2
returnCode=0
result=""
snapRef=com.opsware.compliance.sco.SnapshotResultRef()

ts = twistserver.TwistServer()
auditTaskService = ts.compliance.sco.AuditTaskService
snapshotResultService = ts.compliance.sco.SnapshotResultService


try:
        found=False
        #on recupere notre snapshot result via son id
        filtreSnapR=com.opsware.search.Filter()
        snapRRefs=snapshotResultService.findSnapshotResultRefs(filtreSnapR)
        for snapRRef in snapRRefs:
                if sourceID == str(snapRRef.getId()):
                        snapRef=snapRRef
                        found=True
                else:
                        continue
        if not found:
                result="Impossible de trouver un snapshot avec cet id"
                returnCode=1
        else:#on recupere notre audit task a mettre a jour
                filtreAudit=com.opsware.search.Filter()
                filtreAudit.expression = 'AuditTaskVO.name *=* "%s"' % (auditName)
                auditTRef=auditTaskService.findAuditTaskRefs(filtreAudit)
                auditID=auditTRef[0].getId()
                auditRef=com.opsware.compliance.sco.AuditTaskRef(auditID)
                auditTVO=auditTaskService.getAuditTaskVO(auditRef)
                auditTVO.setSource(snapRef)#on modifie la source
                auditTaskService.update(auditRef,auditTVO,1,1)#on update notre audit task
                result="action effectuee"
except:
        returnCode=1
        result="Impossible de realiser l'action"
print(result)
sys.exit(returnCode)
