#!/usr/bin/env python
# -*- coding: utf-8 -*-
# validate_mtls.py  --  WLST mutual-TLS sanity checker

from java.lang import System
from java.util import Arrays

# ---------------- editable section -----------------------------------
ADMIN_URL  = 't3://192.168.210.146:7001'
ADMIN_USER = 'weblogic'
ADMIN_PW   = 'welcome1'

NAP_NAME     = 'https-app'          # Network Access Point name
MTLS_SERVERS = ['managed']          # servers that MUST run with mTLS
# ---------------------------------------------------------------------

# ----- tiny helpers --------------------------------------------------
def h(text):
    print '\n' + '-' * 64
    print text
    print '-' * 64

def p(msg):      print '   ' + msg
def ok(msg,val): p('[ OK ] %-32s %s'  % (msg,val))
def fl(msg,val): p('[FAIL] %-30s %s' % (msg,val))
def na(msg, val=None):  p('[N/A ] ' + msg)  # Fixed to handle optional second param

# ---------- connect --------------------------------------------------
connect(ADMIN_USER, ADMIN_PW, ADMIN_URL)
dom = cmo.getName()
print '=' * 69
print ' mTLS VALIDATION REPORT  domain=%s  millis=%s' % (dom, System.currentTimeMillis())
print '=' * 69

# ---------- realm-level checks ---------------------------------------
ias = cmo.getSecurityConfiguration().getDefaultRealm()\
        .lookupAuthenticationProvider('DefaultIdentityAsserter')

h('DefaultIdentityAsserter')
active = list(ias.getActiveTypes())
if 'X.509' in active: ok('X.509 in ActiveTypes', str(active))
else:                 fl('X.509 in ActiveTypes', str(active))

vu = ias.isVirtualUserAllowed()
if vu: ok('Virtual users allowed', str(vu))
else: fl('Virtual users allowed', str(vu))

# ---------- per-server checks ----------------------------------------
for s in cmo.getServers():
    name = s.getName()
    must = name in MTLS_SERVERS
    h('SERVER: ' + name)

    # --- keystores ----------------------------------------------------
    ksMode = s.getKeyStores()
    idFile,idTyp = s.getCustomIdentityKeyStoreFileName(), s.getCustomIdentityKeyStoreType()
    trFile,trTyp = s.getCustomTrustKeyStoreFileName(),    s.getCustomTrustKeyStoreType()

    if must:
        (ok if ksMode=='CustomIdentityAndCustomTrust' else fl)('Keystores mode', ksMode)
        (ok if idFile and idTyp else fl)('Identity KS', '%s (%s)'%(idFile,idTyp))
        (ok if trFile and trTyp else fl)('Trust KS',    '%s (%s)'%(trFile,trTyp))
    else:
        na('Keystores not validated')

    # --- SSL MBean ----------------------------------------------------
    ssl = s.getSSL()
    if ssl is None:
        fl('SSL MBean', 'missing')
    else:
        tw,enf = ssl.isTwoWaySSLEnabled(), ssl.isClientCertificateEnforced()
        if must:
            (ok if tw  else fl)('SSL TwoWay', str(tw))
            # *** expect Enforced == True for server-level SSL ***
            (ok if enf else fl)('SSL ClientCertEnforced', str(enf))
        else:
            na('SSL TwoWay / Enforced')

    # --- Network Access Point ----------------------------------------
    nap = getMBean('/Servers/%s/NetworkAccessPoints/%s' % (name,NAP_NAME))
    if nap is None:
        (fl if must else na)('Channel %s not found' % NAP_NAME, '')
    else:
        twc,enc = nap.isTwoWaySSLEnabled(), nap.isClientCertificateEnforced()
        if must:
            (ok if twc  else fl)('NAP TwoWay',  str(twc))
            (ok if not enc else fl)('NAP ClientCertEnforced', str(enc))
        else:
            na('NAP TwoWay / Enforced')

disconnect()
exit()