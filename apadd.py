import sys
import time
import radkit_client
import radkit_genie
import asyncio

async def add_devices(dvs,
                     user,
                     password,
                     base_url="https://localhost:8081/api/v1",
                     admin_name="superadmin",
                     admin_password="H0M3world#"):

    from radkit_remote.serviceapi import Service
    devices = []
    for row in dvs:
        devices.append({
            "name": row["hostname"],
            "host": row["address"],
            "description":row["description"],
            "deviceType": "IOS",
            "terminal": {
                "port": row["port"],

                "connectionMethod": row["protocol"].upper(),
                "username": user,
                "password": password
            }
        })
    async with Service.create(
            base_url=base_url,
            admin_name=admin_name,
            admin_password=admin_password,
            http_client_kwargs=dict(verify=False),
    ) as service:
        result = await service.device_create_bulk(devices)
        print(result)

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

        #This is a 9800 WLC. Let's take a look at the default ap profile to see the AP credentials
        profileconfig=currentdevice.exec("show run | s default-ap-profile").wait()
        profilelinebyline=profileconfig.result.text.split("\n")
        profilelinebroken=""
        for line in profilelinebyline:
            if 'mgmtuser' in line:
                profilelinebroken=line.split()
                #This is the AP username
                print("new line:" + profilelinebroken[2])
        #  Let's figure out its AP list
        apsumoutput=currentdevice.exec("show ap summary").wait()
        apsumgenie=radkit_genie.parse(apsumoutput,os="iosxe")
        print(apsumoutput.result.text)
        for apname in apsumgenie[currentdev]["show ap summary"].data['ap_name']:
            print("ap name="+apname)
            print(apsumgenie[currentdev]["show ap summary"].data['ap_name'][apname]['ap_ip_address'])
            listofdevicetoadd=[]
            listofdevicetoadd.append(dict(hostname=apname,protocol="ssh",address=apsumgenie[currentdev]["show ap summary"].data['ap_name'][apname]['ap_ip_address'],description=apname,port=22))
            asyncio.run(add_devices(listofdevicetoadd,profilelinebroken[2],"Wireless123#"))

