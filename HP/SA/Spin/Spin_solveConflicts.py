#!/opt/opsware/bin/python2
#script to allow automatic resolve for conflicts in a mesh

import sys
sys.path.append("/opt/opsware/pylibs2")
from coglib import spinwrapper
spin = spinwrapper.SpinWrapper("http://localhost:1007")
lconflicts=spin.multimaster.getConflicts()
coreID=input("Which core should be use as reference to solve all conflicts:(Enter core agent id)")
print("Before autoResolve: "+str(len(lconflicts)))
spin.multimaster.autoResolve()
lconflicts=spin.multimaster.getConflicts()
print("After autoResolve: "+str(len(lconflicts)))
for confl in lconflicts["conflicts"]:
        print(confl["tran_id"])
		try:
			spin.multimaster.syncTransaction(tran_id=confl["tran_id"],source_core_id=coreID)
		except:
			error="can't sync"
		try:
			spin.multimaster.markResolved(tran_id=confl["tran_id"])
		except:
			error="can't mark resolved"
lconflicts=spin.multimaster.getConflicts()
print("After manualResolve: "+str(len(lconflicts)))
