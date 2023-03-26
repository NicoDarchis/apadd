import sys
import time
import radkit_client
import radkit_genie


client = radkit_client.sso_login("ndarchis@cisco.com")
service = client.service("o3ca-gxlk-fysc")

service.update_inventory().wait()
for currentdev in service.inventory:
    #currentdev is the current device name inside radkit
    currentdevice = service.inventory[currentdev]
    currentdevice.exec("term len 0").wait()
    #We figure out what kind of device is the current device.
    devicetype=radkit_genie.fingerprint(currentdevice,"iosxe")
    if 'cat9800' in devicetype[currentdev]['platform']:
        #This is a 9800 WLC. Let's figure out its AP list
        apsumoutput=currentdevice.exec("show ap summary").wait()
        apsumgenie=radkit_genie.parse(apsumoutput,os="iosxe")
        print(apsumoutput.result.text)
        print(apsumgenie[currentdev]["show ap summary"].data['ap_name'])
