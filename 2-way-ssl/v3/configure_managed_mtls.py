#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  WebLogic 14c mTLS helper - $ORACLE_HOME/oracle_common/common/bin/wlst.sh  configure_managed_mtls.py
# ---------------------------------------------------------------------------
#  • Discovers managed servers
#  • Applies baseline where missing, restarts changed servers
#  • Connection details via CLI -> ENV -> interactive prompt (password masked)
# ---------------------------------------------------------------------------

from time import sleep
import sys, os, getopt, getpass
from java.lang import System

# ── Baseline constants ──────────────────────────────────────────────────────
SSL_PORT               = 7002
KEYSTORE_MODE_EXPECTED = 'CustomIdentityAndCustomTrust'
IDENTITY_P12           = '/home/dev/domains/DEV/keystores/server-identity.p12'
IDENTITY_PW            = 'wls12345'
TRUST_JKS              = '/home/dev/domains/DEV/keystores/truststore.jks'
TRUST_PW               = ''
PRIVATE_KEY_ALIAS      = 'servercert'
TWO_WAY_ENABLED        = True
CERT_ENFORCED          = False

# ── Helpers ─────────────────────────────────────────────────────────────────
def hidden_input(prompt_txt):
    console = System.console()
    if console:
        chars = console.readPassword(prompt_txt)
        return ''.join(chars) if chars else ''
    return getpass.getpass(prompt_txt)

def get_admin_details():
    cli = {}
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], '',
            ['admin-user=', 'admin-pass=', 'admin-host=', 'admin-port='])
        for opt, val in opts:
            cli[opt] = val
    except getopt.GetoptError as exc:
        print('Option parsing error:', exc); sys.exit(2)

    user = cli.get('--admin-user') or os.getenv('ADMIN_USER') \
           or raw_input('Admin user            : ')
    pw   = cli.get('--admin-pass') or os.getenv('ADMIN_PASS') \
           or hidden_input('Admin password        : ')
    host = cli.get('--admin-host') or os.getenv('ADMIN_HOST') \
           or raw_input('Admin server host/IP  : ')
    port = cli.get('--admin-port') or os.getenv('ADMIN_PORT') \
           or raw_input('Admin server port     : ')

    return user.strip(), pw, host.strip(), str(port).strip()

# ── 0. Connect ──────────────────────────────────────────────────────────────
ADMIN_USER, ADMIN_PW, ADMIN_HOST, ADMIN_PORT = get_admin_details()
connect(ADMIN_USER, ADMIN_PW, 't3://%s:%s' % (ADMIN_HOST, ADMIN_PORT))

# ── 1. Discover managed servers ─────────────────────────────────────────────
domainConfig()
managed = [s.getName() for s in cmo.getServers() if s.getName() != 'AdminServer']
if not managed:
    print('No managed servers found.'); disconnect(); exit()

print('\nManaged servers discovered:')
for idx, svr in enumerate(managed, 1):
    print('  %d) %s' % (idx, svr))

sel = raw_input('\nApply/verify mTLS on (a)ll or enter comma-separated numbers? [a]: ').strip()
targets = managed if sel.lower() in ('', 'a', 'all') else \
          [managed[int(i)-1] for i in sel.split(',')]

# ── 2. Audit routine ────────────────────────────────────────────────────────
def inspect(server):
    cd('/Servers/%s' % server)
    data = {
        'keystore_mode': (get('KeyStores'), KEYSTORE_MODE_EXPECTED),
        'identity_path': (get('CustomIdentityKeyStoreFileName'), IDENTITY_P12),
        'identity_type': (get('CustomIdentityKeyStoreType'), 'PKCS12'),
        'trust_path'   : (get('CustomTrustKeyStoreFileName'), TRUST_JKS),
        'trust_type'   : (get('CustomTrustKeyStoreType'), 'JKS'),
    }
    cd('/Servers/%s/SSL/%s' % (server, server))
    data.update({
        'ssl_enabled'  : (cmo.isEnabled(), True),
        'ssl_port'     : (cmo.getListenPort(), SSL_PORT),
        'pk_alias'     : (cmo.getServerPrivateKeyAlias(), PRIVATE_KEY_ALIAS),
        'two_way'      : (cmo.isTwoWaySSLEnabled(), TWO_WAY_ENABLED),
        'cert_enforced': (cmo.isClientCertificateEnforced(), CERT_ENFORCED),
    })
    for k, (act, exp) in data.items():
        data[k] = (act, exp, (str(act) == str(exp)))
    return data

def show_report(results, title):
    print('\n' + title); print('-' * len(title))
    for svr, attrs in results.items():
        print('\n%s' % svr)
        for k, (act, exp, ok) in attrs.items():
            status = 'OK' if ok else 'MISSING'
            act_disp = '<unset>' if act in ('', None) else act
            print('  %-14s : %-25s  [%s]' % (k, act_disp, status))
    print('-' * len(title))

# ── 3. Pre-change audit ─────────────────────────────────────────────────────
pre = {s: inspect(s) for s in targets}
show_report(pre, 'Current mTLS Settings')

if all(all(v[2] for v in a.values()) for a in pre.values()):
    print('\nAll selected servers already meet the baseline. Nothing to do.')
    disconnect(); exit()

# ── 4. Apply missing settings ───────────────────────────────────────────────
edit(); startEdit()
for svr, attrs in pre.items():
    if all(v[2] for v in attrs.values()):
        continue
    print('\nApplying baseline to %s …' % svr)
    cd('/Servers/%s' % svr)
    set('KeyStores', KEYSTORE_MODE_EXPECTED)
    set('CustomIdentityKeyStoreFileName',   IDENTITY_P12)
    set('CustomIdentityKeyStoreType',       'PKCS12')
    set('CustomIdentityKeyStorePassPhrase', IDENTITY_PW)
    set('CustomTrustKeyStoreFileName',      TRUST_JKS)
    set('CustomTrustKeyStoreType',          'JKS')
    set('CustomTrustKeyStorePassPhrase',    TRUST_PW)
    cd('/Servers/%s/SSL/%s' % (svr, svr))
    set('Enabled', 'true')
    set('ListenPort', SSL_PORT)
    set('ServerPrivateKeyAlias',      PRIVATE_KEY_ALIAS)
    set('ServerPrivateKeyPassPhrase', IDENTITY_PW)
    set('TwoWaySSLEnabled',           TWO_WAY_ENABLED)
    set('ClientCertificateEnforced',  CERT_ENFORCED)
save(); activate(block='true')

# ── 5. Restart changed servers ──────────────────────────────────────────────
changed = [s for s, a in pre.items() if not all(v[2] for v in a.values())]
for s in changed:
    print('\nRestarting %s …' % s)
    shutdown(s, 'Server', ignoreSessions='true', timeOut=60)
    start(s); sleep(10); state(s, 'Server')

# ── 6. Post-change audit ────────────────────────────────────────────────────
post = {s: inspect(s) for s in targets}
show_report(post, 'Updated mTLS Settings (after restart)')

print('\nDone.')
disconnect(); exit()
