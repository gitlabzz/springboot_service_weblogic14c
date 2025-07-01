#!/usr/bin/env python
# -*- coding: utf-8 -*-

# $ORACLE_HOME/oracle_common/common/bin/wlst.sh  configure_managed_mtls.py
# ---------------------------------------------------------------------------
#  Two-Way SSL (optional client cert) for a 14c managed server
#    • custom identity + trust keystores
#    • server SSL alias + 2-way flags
#    • enable SSL listen port 7002
#    • graceful restart of the managed server
# ---------------------------------------------------------------------------
from time import sleep

connect('weblogic', 'welcome1', 't3://192.168.210.146:7001')

MANAGED  = 'managed'                 # managed-server name
PORT     = 7002                      # SSL listen port

ID_P12   = '/home/dev/domains/DEV/keystores/server-identity.p12'
ID_PW    = 'wls12345'
TRUST    = '/home/dev/domains/DEV/keystores/truststore.jks'
TRUST_PW = ''                        # empty only if JKS really has no password

# ── 1. Server-level: keystores ─────────────────────────────────────────────
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

# ── 2. SSLMBean: enable SSL port + 2-way SSL flags ─────────────────────────
edit(); startEdit()
cd('/Servers/%s/SSL/%s' % (MANAGED, MANAGED))

# --- SSL listen port ---
set('Enabled', 'true')          # == “SSL Listen Port Enabled”
set('ListenPort', PORT)         # == “SSL Listen Port” = 7002

# --- MTLS settings ---
set('ServerPrivateKeyAlias',      'servercert')
set('ServerPrivateKeyPassPhrase', ID_PW)
set('TwoWaySSLEnabled',           True)     # request client cert
set('ClientCertificateEnforced',  False)    # do NOT abort handshake

save(); activate(block='true')

# ── 3. Verification BEFORE restart ─────────────────────────────────────────
print('\n--- Current SSL settings on %s ---' % MANAGED)
print(' SSL Enabled    :', cmo.isEnabled())
print(' SSL ListenPort :', cmo.getListenPort())
print(' Two-Way SSL    :', cmo.isTwoWaySSLEnabled())
print(' Cert Enforced  :', cmo.isClientCertificateEnforced())

# ── 4. Graceful restart ────────────────────────────────────────────────────
print('\nRestarting managed server so the SSL subsystem reloads …')
shutdown(MANAGED, 'Server', ignoreSessions='true', timeOut=60)
start(MANAGED)

sleep(10)         # wait for RUNNING
state(MANAGED, 'Server')

print('\nAll done.')
disconnect(); exit()