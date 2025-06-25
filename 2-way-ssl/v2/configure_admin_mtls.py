#!/usr/bin/env python
# -*- coding: utf-8 -*-

# $ORACLE_HOME/oracle_common/common/bin/wlst.sh  configure_admin_mtls.py
# ---------------------------------------------------------------------------
#  WebLogic 14c  – enable X.509 identity assertion & virtual users
#  Scope : domain-wide (runs against the AdminServer)
# ---------------------------------------------------------------------------
from java.lang import String
from jarray   import array

ADMIN_URL  = 't3://192.168.210.146:7001'
ADMIN_USER = 'weblogic'
ADMIN_PW   = 'welcome1'

connect(ADMIN_USER, ADMIN_PW, ADMIN_URL)

print('\n--- 1. Enable X.509 + virtual users on DefaultIdentityAsserter ----------')
edit(); startEdit()

realm = cmo.getSecurityConfiguration().getDefaultRealm()
ias   = realm.lookupAuthenticationProvider('DefaultIdentityAsserter')

# a) X.509 must be in ActiveTypes
wantedTypes = ['X.509', 'AuthenticatedUser', 'weblogic-jwt-token']
ias.setActiveTypes(array(wantedTypes, String))

# b) allow transient (certificate) users
ias.setVirtualUserAllowed(True)

save(); activate(block='true')

print('\n--- 2. Verification ------------------------------------------------------')
print('ActiveTypes          :', list(ias.getActiveTypes()))
print('VirtualUserAllowed   :', ias.isVirtualUserAllowed())
print('Done – NO restart needed on AdminServer.\n')

disconnect(); exit()
