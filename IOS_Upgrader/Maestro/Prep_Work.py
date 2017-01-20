__author__ = 'jacurran'

##################################################

def IOS_upgrade_prep(network_device,
                     file_source="ens-sj1.cisco.com://users/ftp/images"):
    HALT = False
    error = False

    if network_device.current_IOS_file == network_device.new_IOS_file:
        error = "{} is already running {}!".format(network_device.name,network_device.new_IOS_file)
        HALT = True

    if not HALT:
        try:
            network_device.login()
        except:
            error = "SSH v2 is not functioning on {}.".format(network_device.name)
            HALT  = True
        else:
            network_device.get_prompt()
            if "#" not in network_device.prompt:
                error = "Device has ARBAC issues, logon was not granted enable mode."
                HALT = True

    if not HALT:
        network_device.determine_media()

        network_device.IOS_reclaim_space(network_device.primary_copy_location)
        for location in network_device.available_media:
            network_device.IOS_reclaim_space(location)

        IOS_copy_error = network_device.file_upload(new_file=network_device.new_IOS_file,
                                                    md5_hash_provided=network_device.IOS_md5_hash,
                                                    file_source=file_source)
        if IOS_copy_error:
            error = "There was an issue copying IOS {} on device {}".format(network_device.new_IOS_file,
                                                                            network_device.name)
            HALT = True

    if not HALT and network_device.new_FPD_file:
        network_device.fpd_reclaim_space(network_device.primary_copy_location)
        for location in network_device.available_media:
            network_device.fpd_reclaim_space(location)

        FPD_copy_error = network_device.file_upload(new_file=network_device.new_FPD_file,
                                                    md5_hash_provided=network_device.FPD_md5_hash,
                                                    file_source=file_source)
        if FPD_copy_error:
            error = "There was an issue copying FPD {} on device {}".format(network_device.new_FPD_file,
                                                                            network_device.name)
            HALT = True

    if not HALT:
        network_device.backup_run_config()
        network_device.change_boot_vars()
    network_device.logout()

    if error:
        return error
    elif network_device.new_FPD_file:
        return "Device {}\n\nSuccessfully prepped for:\nIOS {} &\nFPD file {}"\
            .format(network_device.name,
                    network_device.new_IOS_file,
                    network_device.new_FPD_file)
    else:
        return "Device {}\n\nSuccessfully prepped for:\nIOS {}"\
            .format(network_device.name,
                    network_device.new_IOS_file)

##################################################

def ROMMON_upgrade_prep(network_device,
                        file_source="ens-sj1.cisco.com://users/ftp/images"):
    HALT = False
    error = ""

    if network_device.current_IOS_file == network_device.new_IOS_file:
        error = "{} is already running {}!".format(network_device.name,network_device.new_IOS_file)
        HALT = True

    if not HALT:
        if not network_device.ROMMON_file:
            error = "The design standards don't specify a new ROMMON file for:\n{}.".format(network_device.name)
            HALT = True

    if not HALT:
        try:
            network_device.login()
        except:
            error = "SSH v2 is not functioning on {}.".format(network_device.name)
            HALT  = True
        else:
            network_device.get_prompt()
            if "#" not in network_device.prompt:
                error = "Device has ARBAC issues, logon was not granted enable mode."
                HALT = True

    if not HALT:
        network_device.determine_media()

        network_device.ROMMON_reclaim_space(network_device.primary_copy_location)
        for location in network_device.available_media:
            network_device.ROMMON_reclaim_space(location)

        ROMMON_copy_error = network_device.file_upload(new_file=network_device.ROMMON_file,
                                                       md5_hash_provided=network_device.ROMMON_md5_hash,
                                                       file_source=file_source)
        if ROMMON_copy_error:
            error = "There was an issue copying ROMMON {} on device {}".format(network_device.ROMMON_file,
                                                                               network_device.name)
            HALT = True

    if not HALT:
        network_device.backup_run_config()
        network_device.sys_prepare_ROMMON()

    network_device.logout()

    if error:
        return error

    else:
        return "Device {}\n\nSuccessfully prepped for:\nROMMON {}"\
            .format(network_device.name,
                    network_device.ROMMON_file)
