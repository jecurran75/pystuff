from Factory import Sales_Order

__author__ = 'jacurran'

##################################################

hostname = raw_input("Hostname: ").strip()
network_device = Sales_Order.specs(name=hostname)

if network_device.is_alive():
    try:
        network_device.login()
    except:
        print "SSH v2 is not functioning on {}.".format(network_device.name)
    else:
        network_device.get_prompt()
        if "#" not in network_device.prompt:
            print "Device has ARBAC issues, logon was not granted enable mode."
        else:
            network_device.SNMPv3_config()
        network_device.logout()

else:
    print "{} is not replying to pings.".format(hostname)
