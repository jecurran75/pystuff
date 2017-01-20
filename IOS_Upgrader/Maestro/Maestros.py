from IOS_Upgrader.Factory import Sales_Order
from IOS_Upgrader.Factory.Get_HW_SW import Get_HW_SW
from IOS_Upgrader.Factory.Standards_Guru import get_standards_info
from Prep_Work import IOS_upgrade_prep, ROMMON_upgrade_prep

__author__ = 'jacurran'

##################################################

def db_doorway(hostname):
    """
    This function will assist the NO2 AL to update its host DB entries.

    design_tuple = (recommend_IOS_file,
                    recommend_IOS_md5,
                    recommend_IOS_FPD_file,
                    recommend_IOS_FPD_md5,
                    recommend_rommon_file,
                    recommend_rommon_md5,
                    LD_IOS_file,
                    LD_IOS_md5,
                    LD_IOS_FPD_file,
                    LD_IOS_FPD_md5,
                    acceptable_ios_file)

    db_tuple = (hw_PID,
                sup_PID,
                Current_IOS,
                recommend_IOS_file,
                recommend_IOS_md5,
                recommend_IOS_FPD_file,
                recommend_IOS_FPD_md5,
                recommend_rommon_file,
                recommend_rommon_md5,
                LD_IOS_file,
                LD_IOS_md5,
                LD_IOS_FPD_file,
                LD_IOS_FPD_md5,
                acceptable_ios_file)
    """
    hw_PID, sup_PID, Current_IOS = Get_HW_SW(hostname)
    design_tuple = get_standards_info(hostname=hostname,
                                      hw_pid=hw_PID,
                                      sup_pid=sup_PID,
                                      xldir="./IOS_Upgrader")
                                    #xldir is the directory where /Factory is placed.
    if design_tuple:
        db_tuple = (hw_PID,sup_PID,Current_IOS) + design_tuple
        return db_tuple
    else:
        return design_tuple

##################################################

def IOS_Maestro(hostname,
                LD=False,
                acceptable_IOS_OK=True,
                CR=None,
                file_source="ens-sj1.cisco.com://users/ftp/images"):
    result = ""
    sufficient_ROMMON = True

    HW_PID,Sup_PID,current_IOS = Get_HW_SW(hostname)
    design_tuple = get_standards_info(hostname=hostname,
                                      hw_pid=HW_PID,
                                      sup_pid=Sup_PID,
                                      xldir="./IOS_Upgrader")
                                    # xldir is the directory where /Factory is placed
                                    # relative to upgrade_maestro.py.


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

        if current_IOS == LD_IOS_file and LD:
            result = "Device {}:\nCurrently running Limited Deployment IOS:\n{}".format(hostname,LD_IOS_file)

        elif current_IOS == recommended_IOS_file and not LD:
            result = "Device {}:\nCurrently running recommended IOS:\n{}".format(hostname,recommended_IOS_file)

        elif current_IOS == acceptable_IOS_file and acceptable_IOS_OK and not LD:
            result = "Device {}:\nCurrently running the acceptable IOS:\n{}.".format(hostname,acceptable_IOS_file)+\
                         "\n\nPlease consider upgrading to:\n{}.".format(recommended_IOS_file)

        else:
            if not LD and not CR:
                result = "IOS Upgrade Required, will use:\n{}\nOnce your CR is approved.".format(recommended_IOS_file)

            elif LD and not CR:
                if LD_IOS_file:
                    result = "IOS Upgrade Required, will use LD image:\n{}\nOnce your CR is approved.".format(LD_IOS_file)
                else:
                    result = "This device is flagged as LD but there is currently no approved LD image."+\
                             "\nPlease consult with the design team."

            elif LD and CR and LD_IOS_file:
                intro = "This device is flagged as limited deployment."+\
                        "\nIOS Selected:\n{}".format(LD_IOS_file)

                network_device = Sales_Order.specs(name=hostname,
                                                   HW_PID=HW_PID,
                                                   Sup_PID=Sup_PID,
                                                   current_IOS_file=current_IOS,
                                                   new_IOS_file=LD_IOS_file,
                                                   IOS_md5_hash=design_tuple[7],
                                                   new_FPD_file=design_tuple[8],
                                                   FPD_md5_hash=design_tuple[9],
                                                   ROMMON_file=design_tuple[4],
                                                   ROMMON_md5_hash=design_tuple[5])

                if network_device.ROMMON_file:
                    sufficient_ROMMON = network_device.ROMMON_Compare()


                if not sufficient_ROMMON:
                    result = "ROMMON Upgrade required!"
                    result = ROMMON_upgrade_prep(network_device=network_device,
                                                 file_source=file_source)

                else:
                    result = IOS_upgrade_prep(network_device=network_device,
                                              file_source=file_source)
                    result = intro+"\n\n"+result


            elif CR:
                intro = "IOS Selected:\n{}.".format(recommended_IOS_file)

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

                if network_device.ROMMON_file:
                    sufficient_ROMMON = network_device.ROMMON_Compare()

                if not sufficient_ROMMON:
                    result = "ROMMON Upgrade required!"
                    result = ROMMON_upgrade_prep(network_device=network_device,
                                                 file_source=file_source)

                else:
                    result = IOS_upgrade_prep(network_device=network_device,
                                              file_source=file_source)
                    result = intro+"\n\n"+result

    return result

##################################################

#if __name__ == "__main__":
