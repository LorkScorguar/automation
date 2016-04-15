#!/opt/opsware/bin/python2
#simple sample on how to get a package from spin

import sys
sys.path.append("/opt/opsware/pylibs2")
from coglib import spinwrapper
pid=input("Enter package id:")
spin = spinwrapper.SpinWrapper("http://localhost:1007")
spin.Unit.get(id=pid)
