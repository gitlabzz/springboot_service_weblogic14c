#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configure_managed_mtls.py  –  WebLogic 14c managed-server SSL setup
# ---------------------------------------------------------------------------
#  • collects Admin-Server creds
#  • enables SSL listen port 7002 + mTLS flags
#  • configures custom keystores
#  • graceful restart of the managed server
# ---------------------------------------------------------------------------

from time import sleep
import sys, os, getopt, getpass
from java.lang import System

# ────────────────────────────────────────────────────────────────────────────
#  Secure prompt helper (no echo)
# ────────────────────────────────────────────────────────────────────────────
def prompt_hidden(prompt_text):
    """
    Read a password without echoing to the terminal.
    Tries java.io.Console.readPassword() first; falls back to getpass.
    """
    console = System.console()
    if console:                                                  # preferred path
        char_array = console.readPassword(prompt_text)
        return ''.join(char_array) if char_array else ''
    else:                                                        # fallback
        return getpass.getpass(prompt_text)

# ────────────────────────────────────────────────────────────────────────────
#  Collect Admin-Server connection details: CLI → ENV → PROMPT
# ────────────────────────────────────────────────────────────────────────────
def get_admin_details():
    cli_user = cli_pass = cli_host = cli_port = None

    # --- 1. command-line ----------------------------------------------------
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], '',
            ['admin-user=', 'admin-pass=', 'admin-host=', 'admin-port='])
        for opt, val in opts:
            if   opt == '--admin-user':  cli_user = val
            elif opt == '--admin-pass':  cli_pass = val
            elif opt == '--admin-host':  cli_host = val
            elif opt == '--admin-port':  cli_port = val
    except getopt.GetoptError as exc:
        print('Option parsing error:', exc)
        sys.exit(2)

    # --- 2. environment -----------------------------------------------------
    user = cli_user or os.getenv('ADMIN_USER')
    pw   = cli_pass or os.getenv('ADMIN_PASS')
    host = cli_host or os.getenv('ADMIN_HOST')
    port = cli_port or os.getenv('ADMIN_PORT')

    # --- 3. interactive -----------------------------------------------------
    if not user:
        user = raw_input('Admin user            : ')
    if not pw:
        pw = prompt_hidden('Admin password        : ')
    if not host:
        host = raw_input('Admin server host/IP  : ')
    if not port:
        port = raw_input('Admin server port     : ')

    return user.strip(), pw, host.strip(), str(port).strip()

# ────────────────────────────────────────────────────────────────────────────
#  0. Connect to Admin Server
#  connect('weblogic', 'welcome1', 't3://192.168.210.146:7001')
# ────────────────────────────────────────────────────────────────────────────
ADMIN_USER, ADMIN_PW, ADMIN_HOST, ADMIN_PORT = get_admin_details()
connect(ADMIN_USER, ADMIN_PW, 't3://%s:%s' % (ADMIN_HOST, ADMIN_PORT))

# ────────────────────────────────────────────────────────────────────────────
#  1. constants for managed-server SSL setup
# ────────────────────────────────────────────────────────────────────────────
MANAGED  = 'managed'                 # managed-server name
SSL_PORT = 7002                      # SSL listen port to enable

ID_P12   = '/home/dev/domains/DEV/keystores/server-identity.p12'
ID_PW    = 'wls12345'
TRUST    = '/home/dev/domains/DEV/keystores/truststore.jks'
TRUST_PW = ''                        # empty only if JKS really has no password

# ────────────────────────────────────────────────────────────────────────────
#  2. ServerMBean: custom keystores
# ────────────────────────────────────────────────────────────────────────────
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

# ────────────────────────────────────────────────────────────────────────────
#  3. SSLMBean: enable SSL port + mTLS flags
# ────────────────────────────────────────────────────────────────────────────
edit(); startEdit()
cd('/Servers/%s/SSL/%s' % (MANAGED, MANAGED))

set('Enabled', 'true')                # “SSL Listen Port Enabled”
set('ListenPort', SSL_PORT)           # “SSL Listen Port”

set('ServerPrivateKeyAlias',      'servercert')
set('ServerPrivateKeyPassPhrase', ID_PW)
set('TwoWaySSLEnabled',           True)   # request client cert
set('ClientCertificateEnforced',  False)  # optional, not enforced

save(); activate(block='true')

# ────────────────────────────────────────────────────────────────────────────
#  4. Verification BEFORE restart
# ────────────────────────────────────────────────────────────────────────────
print('\n--- Current SSL settings on %s ---' % MANAGED)
print(' SSL Enabled    :', cmo.isEnabled())
print(' SSL ListenPort :', cmo.getListenPort())
print(' Two-Way SSL    :', cmo.isTwoWaySSLEnabled())
print(' Cert Enforced  :', cmo.isClientCertificateEnforced())

# ────────────────────────────────────────────────────────────────────────────
#  5. Graceful restart
# ────────────────────────────────────────────────────────────────────────────
print('\nRestarting managed server so the SSL subsystem reloads …')
shutdown(MANAGED, 'Server', ignoreSessions='true', timeOut=60)
start(MANAGED)

sleep(10)
state(MANAGED, 'Server')

print('\nAll done.')
disconnect(); exit()
