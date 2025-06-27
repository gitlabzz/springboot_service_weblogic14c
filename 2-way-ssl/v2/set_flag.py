#!/usr/bin/env python
# -*- coding: utf-8 -*-

# set_flag.py
admin_user = 'weblogic'
admin_password = 'welcome1'
admin_url = 't3://192.168.210.146:7001'

print('Connecting to WebLogic Admin Server...')
connect(admin_user, admin_password, admin_url)

print('Starting edit session...')
edit()
startEdit()

try:
    # Corrected path with uppercase domain name 'DEV'
    mbean_path = '/SecurityConfiguration/DEV/Realms/myrealm/AuthenticationProviders/DefaultIdentityAsserter'
    print('Navigating to MBean: ' + mbean_path)
    cd(mbean_path)

    print('Setting ControlFlag to SUFFICIENT...')
    set('ControlFlag', 'Sufficient')

    print('Saving and activating changes...')
    save()
    activate()
    print('SUCCESS: The ControlFlag has been set.')

except:
    print('ERROR: An error occurred. Undoing changes.')
    # Cleanly stop the edit session without saving changes
    stopEdit('y')
    print('Edit session stopped. Changes have been discarded.')

print('Disconnecting from the server.')
disconnect()
exit()