#!/usr/bin/env python
# -*- coding: utf-8 -*-

# $ORACLE_HOME/oracle_common/common/bin/wlst.sh  configure_managed_mtls.py
# ---------------------------------------------------------------------------
#  Two-Way SSL (optional client cert) for managed14c server
#
#  - custom identity + trust keystores
#  - server SSL alias + 2-way flags
#  - graceful restart of managed server
# ---------------------------------------------------------------------------
from time import sleep
connect('weblogic', 'welcome1', 't3://192.168.210.146:7001')

MANAGED = 'managed'                 # WebLogic server name
HOST    = '192.168.210.147'
PORT    = 7002

ID_P12  = '/home/dev/domains/DEV/keystores/server-identity.p12'
ID_PW   = 'wls12345'
TRUST   = '/home/dev/domains/DEV/keystores/truststore.jks'
TRUST_PW= ''                        # empty password

# ---------- 1. custom keystores --------------------------------------------
edit(); startEdit()
cd('/Servers/%s' % MANAGED)

set('KeyStores', 'CustomIdentityAndCustomTrust')

set('CustomIdentityKeyStoreFileName',   ID_P12)
set('CustomIdentityKeyStoreType',       'PKCS12')
set('CustomIdentityKeyStorePassPhrase', ID_PW)

set('CustomTrustKeyStoreFileName',      TRUST)
set('CustomTrustKeyStoreType',          'JKS')
set('CustomTrustKeyStorePassPhrase',    TRUST_PW)

save(); activate(block='true')

# ---------- 2. server-level SSL flags --------------------------------------
edit(); startEdit()
cd('/Servers/%s/SSL/%s' % (MANAGED, MANAGED))

set('ServerPrivateKeyAlias',        'servercert')
set('ServerPrivateKeyPassPhrase',   ID_PW)
set('TwoWaySSLEnabled',             True)      # request a client cert
set('ClientCertificateEnforced',    False)     # but do NOT abort handshake

save(); activate(block='true')


# ---------- 3. Verification BEFORE restart ---------------------------------
print('\n--- Current settings on %s -----------------------------------------' % MANAGED)
cd('/Servers/%s/SSL/%s' % (MANAGED, MANAGED))
print('Server-SSL  TwoWay=%s  Enforced=%s' %
      (cmo.isTwoWaySSLEnabled(), cmo.isClientCertificateEnforced()))

# ---------- 4. Restart managed server --------------------------------------
print('\nRestarting managed server so the SSL subsystem reloads the keystores …')
shutdown(MANAGED, 'Server', ignoreSessions='true', timeOut=60)
start(MANAGED)

# tiny wait so the JVM reaches RUNNING before we query it
sleep(10)
state(MANAGED, 'Server')

print('\nAll done.')

disconnect(); exit()
