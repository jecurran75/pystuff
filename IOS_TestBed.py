from IOS_Upgrader.Factory import Sales_Order
from IOS_Upgrader.Factory.Get_HW_SW import Get_HW_SW
from IOS_Upgrader.Factory.Standards_Guru import get_standards_info

__author__ = 'jacurran'

##################################################

result = ""

hostname = raw_input("Hostname: ").strip()

HW_PID,Sup_PID,current_IOS = Get_HW_SW(hostname)

design_tuple = get_standards_info(hostname=hostname,
                                  hw_pid=HW_PID,
                                  sup_pid=Sup_PID,
                                  xldir="./IOS_Upgrader")

if HW_PID == "SNMP_ERROR":
    result = "SNMPv3 is not functioning on this device, please correct."

elif not design_tuple:
    result = "Could not find a Maestro compatible design standard for device:\n{}.".format(hostname)

elif current_IOS == "packages.conf":
    result = "Device {}:\nIs using packages.conf.\nThis setup is not supported by this system.".format(hostname)

else:
    recommended_IOS_file = design_tuple[0]
    LD_IOS_file = design_tuple[6]
    acceptable_IOS_file = design_tuple[10]
    #
    network_device = Sales_Order.specs(name=hostname,
                                       HW_PID=HW_PID,
                                       Sup_PID=Sup_PID,
                                       current_IOS_file=current_IOS,
                                       new_IOS_file=recommended_IOS_file,
                                       IOS_md5_hash=design_tuple[1],
                                       new_FPD_file=design_tuple[2],
                                       FPD_md5_hash=design_tuple[3],
                                       ROMMON_file=design_tuple[4],
                                       ROMMON_md5_hash=design_tuple[5])

if result:
    print result


