from Factory import Sales_Order
from Factory.Get_HW_SW import Get_HW_SW
from Factory.Standards_Guru import get_standards_info
from subprocess import call, PIPE, STDOUT

__author__ = 'jacurran'

##################################################

def is_network_alive(hostname):
    args = ("ping -c 1 "+hostname).split()
    if call(args, stdout=PIPE, stderr=STDOUT) == 0:
        return True
    elif call(args, stdout=PIPE, stderr=STDOUT) == 0:
        return True
    else:
        return False

##################################################

def get_console_names(network_device):

    console_list = []
    dead_console_list = []
    live_console_list = []
    accessible_console_list = []
    misconfigured_console_list = []
    incompatible_console_list = []

    raw_hostname = remove_cisco_com(network_device.name)

    console_list.append(raw_hostname+"-con.cisco.com")

    if network_device.Sup_num == 2:
        console_list.append(raw_hostname+"-con2.cisco.com")

    elif network_device.stack_size:
        for i in range (network_device.stack_size):
            console_list.append(raw_hostname+"-con{}.cisco.com".format(i+1))

    elif raw_hostname+"-con1.cisco.com" not in console_list:
        console_list.append(raw_hostname + "-con1.cisco.com")

    for console_name in console_list:
        if is_network_alive(console_name):
            live_console_list.append(console_name)
        else:
            dead_console_list.append(console_name)

    if raw_hostname+"-con.cisco.com" in live_console_list and \
        raw_hostname+"-con1.cisco.com" in dead_console_list:
        dead_console_list.remove(raw_hostname+"-con1.cisco.com")

    if raw_hostname+"-con1.cisco.com" in live_console_list and \
        raw_hostname+"-con.cisco.com" in dead_console_list:
        dead_console_list.remove(raw_hostname+"-con.cisco.com")

    if raw_hostname+"-con.cisco.com" in dead_console_list and \
        raw_hostname+"-con1.cisco.com" in dead_console_list:
        dead_console_list.remove(raw_hostname+"-con1.cisco.com")

    for live_console in live_console_list:
        console_line = Sales_Order.specs(name=live_console)

        console_line.login(quiet=True)
        prompt = console_line.sendcmd("")[-1].strip()
        if prompt == "PARAMIKO INCOMPATIBILITY ERROR":
            incompatible_console_list.append(live_console)
        elif raw_hostname in prompt:
            accessible_console_list.append(live_console)
        elif "-cs" in prompt:
            accessible_console_list.append(live_console)
            dead_console_list = []
        else:
            misconfigured_console_list.append(live_console)
        console_line.logout(quiet=True)

    network_device.accessible_console_list = accessible_console_list
    network_device.misconfigured_console_list = misconfigured_console_list
    network_device.incompatible_console_list = incompatible_console_list
    network_device.dead_console_list = dead_console_list

##################################################

def remove_cisco_com(hostname):
    if ".cisco.com" in hostname:
        index = hostname.index(".cisco.com")
        raw_hostname = hostname[:index]
    else:
        raw_hostname = hostname

    return raw_hostname

##################################################

def reload_IOS(hostname, LD=False):

    HW_PID, Sup_PID, current_IOS = Get_HW_SW(hostname)
    design_tuple = get_standards_info(hostname=hostname,
                                      hw_pid=HW_PID,
                                      sup_pid=Sup_PID,
                                      xldir="./IOS_Upgrader")
    # xldir is the directory where /Factory is placed.

    HALT = False
    result = False

    if HW_PID == "SNMP_ERROR":
        result = "SNMPv3 is not functioning on this device, please correct."

    elif not design_tuple:
        result = "Could not find a Maestro compatible design standard for device:\n{}.".format(hostname)

    elif current_IOS == "packages.conf":
        result = "Device {}:\nIs using packages.conf.\nThis setup is not supported by this system.".format(hostname)

    else:
        recommended_IOS_file = design_tuple[0]
        LD_IOS_file = design_tuple[6]

        if LD:
            network_device = Sales_Order.specs(name=hostname,
                                               HW_PID=HW_PID,
                                               Sup_PID=Sup_PID,
                                               current_IOS_file=current_IOS,
                                               new_IOS_file=LD_IOS_file,
                                               new_FPD_file=design_tuple[8])

        else:
            network_device = Sales_Order.specs(name=hostname,
                                               HW_PID=HW_PID,
                                               Sup_PID=Sup_PID,
                                               current_IOS_file=current_IOS,
                                               new_IOS_file=recommended_IOS_file,
                                               new_FPD_file=design_tuple[2])

        if network_device.current_IOS_file == network_device.new_IOS_file:
            result = "Device is already running {}, aborting!".format(network_device.new_IOS_file)
            HALT = True

        if not HALT:
            network_device.login()
            network_device.determine_media()

            IOS_prestaged = True
            for location in network_device.media_list:
                if not network_device.new_file_there(the_file=network_device.new_IOS_file,
                                                     location=location):
                    IOS_prestaged = False

            if not IOS_prestaged:
                result = "\nNew IOS file {}\nis not fully pre-staged on device {}!\nAborting...".format(
                    network_device.new_IOS_file,network_device.name)
                HALT = True

        if not HALT:
            get_console_names(network_device)

            if network_device.dead_console_list or \
                    network_device.misconfigured_console_list or \
                    network_device.incompatible_console_list:

                if network_device.misconfigured_console_list:
                    print "\nMisconfigured or incorrectly patched list:"
                    for item in network_device.misconfigured_console_list:
                        print item

                if network_device.incompatible_console_list:
                    print "\nPython SSH incompatibility list:"
                    print "(CS line detected but unable to verify correct"
                    print "patching or configuration)\n"
                    for item in network_device.incompatible_console_list:
                        print item

                    print "\nNote: the hosting console server may have"
                    print "a CS Menu that provides access to additional console lines"
                    print "for secondary sups or switch stack members."

                if network_device.dead_console_list:
                    print "\nThe following are assumed to be needed but do not reply to pings:"
                    for item in network_device.dead_console_list:
                        print item

                #answer = raw_input("\nDo you still want to proceed with the reload? (Y/N default = N): ").lower()
                #if answer != "y":
                #    result = "Reload of {} aborted.".format(network_device.name)
                #    HALT = True

        if not HALT:
            print "\nReloading {} now!".format(network_device.name)
            result = network_device.reload()

    return result




