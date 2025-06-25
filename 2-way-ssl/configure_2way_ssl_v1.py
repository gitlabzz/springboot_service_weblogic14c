# $ORACLE_HOME/oracle_common/common/bin/wlst.sh configure_2way_ssl.py

# ---------------------------------------------------------------------------
#  WLST “gold-path” recipe – WebLogic 14c, two-way SSL, one managed server
#  --------------------------------------------------------------------------
#  EXPECTED FILES (already on both hosts):
#    /home/dev/domains/DEV/keystores/server-identity.p12   password  : wls12345
#    /home/dev/domains/DEV/keystores/truststore.jks        password  :  (blank)
#  SERVER CERT ALIAS  : servercert
#  HTTPS channel name : https-app   on 192.168.210.147:7002
# ---------------------------------------------------------------------------

# ---------- 1. connect ------------------------------------------------------
connect('weblogic', 'welcome1', 't3://192.168.210.146:7001')

ls('/Servers')

# ---------- 2. custom keystores on managed ---------------------------------
edit(); startEdit()
cd('/Servers/managed')

set('KeyStores',                         'CustomIdentityAndCustomTrust')

set('CustomIdentityKeyStoreFileName',    '/home/dev/domains/DEV/keystores/server-identity.p12')
set('CustomIdentityKeyStoreType',        'PKCS12')
set('CustomIdentityKeyStorePassPhrase',  'wls12345')

set('CustomTrustKeyStoreFileName',       '/home/dev/domains/DEV/keystores/truststore.jks')
set('CustomTrustKeyStoreType',           'JKS')
set('CustomTrustKeyStorePassPhrase',     '')                # truststore has no pwd

save(); activate(block='true')

# ---------- 3. server-level SSL (alias & 2-way flags) -----------------------
edit(); startEdit()
cd('/Servers/managed/SSL/managed')

set('ServerPrivateKeyAlias',             'servercert')
set('ServerPrivateKeyPassPhrase',        'wls12345')
set('TwoWaySSLEnabled',                  'true')            # request client cert
set('ClientCertificateEnforced',         'false')           # optional at handshake

save(); activate(block='true')

# ---------- 4. HTTPS channel (Network Access Point) -------------------------
edit(); startEdit()
cd('/Servers/managed')

# does the NAP already exist?
if getMBean('/Servers/managed/NetworkAccessPoints/https-app') is None:
    cmo.createNetworkAccessPoint('https-app')
    print('Created Network Access Point  https-app')
else:
    print('Network Access Point  https-app  already present')

cd('/Servers/managed/NetworkAccessPoints/https-app')

set('Protocol',                 'https')      # turns it into HTTPS
set('ListenAddress',            '192.168.210.147')
set('ListenPort',               7002)
set('HttpEnabledForThisProtocol', False)
set('Enabled',                  True)

# mutual-TLS flags live directly on the channel bean
set('TwoWaySSLEnabled',         'true')
set('ClientCertificateEnforced','false')

save(); activate(block='true')

# ---------- 5. restart managed so it picks everything up --------------------
shutdown('managed', 'Server', ignoreSessions='true', timeOut=60)
start('managed')

print('\n two-way SSL fully configured – check 192.168.210.147:7002\n')
disconnect()
exit()
