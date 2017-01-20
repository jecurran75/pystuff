import commands

__author__ = 'jacurran'

##################################################

sup_OID_list = ["1.3.6.1.2.1.47.1.1.1.1.13.1000",
                "1.3.6.1.2.1.47.1.1.1.1.13.2000",
                "1.3.6.1.2.1.47.1.1.1.1.13.3000",
                "1.3.6.1.2.1.47.1.1.1.1.13.4000",
                "1.3.6.1.2.1.47.1.1.1.1.13.5000",
                "1.3.6.1.2.1.47.1.1.1.1.13.6000",
                "1.3.6.1.2.1.47.1.1.1.1.13.7000",
                "1.3.6.1.2.1.47.1.1.1.1.13.8000",
                "1.3.6.1.2.1.47.1.1.1.1.13.9000",
                "mib-2.47.1.1.1.1.13.9",
                "mib-2.47.1.1.1.1.13.7"]

Valid_Sup_PIDs = ['WS-X45-SUP8-E',
                'WS-X45-SUP7-E',
                "VS-SUP2T-10G",
                "WS-SUP720-3B",
                "VS-S720-10G",
                "WS-SUP32-GE-3B",
                "WS-SUP720-3BXL",
                "ASR1000-RP2",
                "ASR1002-RP1",
                "ASR1000-RP1",
                "NPE-G1",
                "NPE-G2"]

Modular_PIDs = ["WS-C4510R+E",
                "WS-C4507R+E",
                "WS-C6504-E",
                "WS-C6506-E",
                "WS-C6509-E",
                "WS-C6509-V-E",
                "C6807-XL",
                "CISCO7606",
                "ASR1002",
                "ASR1004",
                "ASR1006",
                "CISCO7204VXR",
                "CISCO7206VXR"]

Non_Modular_PIDs = ["C6880-X",
                    "WS-C4948E",
                    "WS-C4948",
                    "WS-C4948E-F",
                    "WS-C4948-10GE",
                    "ISR4451-X/K9",
                    "IE-3010-16S-8PC",
                    "ME-3400E-24TS-M",
                    "ME-3800X-24FS-M",
                    "WS-C4500X-16",
                    "WS-C4500X-32",
                    "WS-C4900M",
                    "3725",
                    "3845",
                    "CISCO3845",
                    "CISCO3945-CHASSIS",
                    "CISCO2901/K9",
                    "CISCO2911/K9",
                    "CISCO2951/K9",
                    "CISCO2811",
                    "2811",
                    "2611XM",
                    "SM-ES3G-16-P",
                    "SM-ES3G-24-P",
                    "WS-C3560-12PC-S",
                    "WS-C3560CX-12PC-S",
                    "CISCO891W-AGN-A-K9",
                    "CISCO892W-AGN-E-K9",
                    "WS-C3850-48P",
                    "WS-C3850-48U",
                    "WS-C3750-24PS-S",
                    "WS-C3750-48PS-S",
                    "WS-C3750E-24TD-E",
                    "WS-C3750E-48PD-EF",
                    "WS-C3750E-48PD-SF",
                    "WS-C3750G-12S-S",
                    "WS-C3750G-24PS-S",
                    "WS-C3750G-24PS-E",
                    "WS-C3750G-24TS-S1U",
                    "WS-C3750G-48PS-S",
                    "WS-C3750G-48PS-E",
                    "WS-C3750G-48TS-S",
                    "WS-C3750X-24P-S",
                    "WS-C3750X-24S-S",
                    "WS-C3750X-24T-S",
                    "WS-C3750X-24T-L",
                    "WS-C3750X-48P-L",
                    "WS-C3750X-48P-S",
                    "WS-C3750X-48T-S",
                    "WS-C3750X-48PF-E",
                    "WS-C3750X-48PF-L",
                    "WS-C3750X-48PF-S"]

All_Known_HW_PIDs = Modular_PIDs + Non_Modular_PIDs

SNMP_errors = ['irectory',
               'am',
               'I',
               'imeou',
               'yp',
               'ey',
               'bject',
               'NMPv2-SMI::mib-2.47.1.1.1.1.13.',
               'rmon.19.6.']

SNMPv3_login = ["network-v3user","D0ntPr1nT4mor"] #[SNMP_v3_user,SNMP_v3_password]

##################################################


def SNMP_OS_Call(hostname,oid):
    OS_Call = commands.getoutput(
        '/usr/bin/snmpbulkwalk -v3 -l authNopriv -u {} -a SHA -A {} {} {}'
            .format(SNMPv3_login[0],SNMPv3_login[1],hostname,oid))
    return OS_Call

##################################################

def Get_SW(hostname,SW_OID=".1.3.6.1.2.1.16.19.6.0"):
    # Get the IOS filename via SNMP
    ios_file = SNMP_OS_Call(hostname, oid=SW_OID).split()[-1][1:-1].split(":")[-1]
    #
    # Some devices have subdirectories for the IOS file, correct for that.
    if "/" in ios_file:
        ios_file = ios_file.split("/")[-1]
    #
    # Flag SNMP Errors
    if ios_file in SNMP_errors:
        ios_file = "SNMP_ERROR"
    #
    # ASRs have a bug that cuts off part of the .bin, correct for that
    if ios_file[-3:] == ".bi" and ".bin" not in ios_file:
        ios_file = ios_file + "n"
    if ios_file[-2:] == ".b" and ".bin" not in ios_file:
        ios_file = ios_file + "in"
    #
    return ios_file

##################################################

def Get_Sup_PID(hostname):
    # Tries to get a known valid supervisor PID using a list of possible SNMP OID values.

    Sup_PID = None
    for OID in sup_OID_list:
        # Get the supervisor PID via SNMP
        Sup_PID = SNMP_OS_Call(hostname, oid=OID).split()[-1][1:-1]
        #
        # Checks against a valid results list, stops search once one is found.
        if Sup_PID in Valid_Sup_PIDs:
            break
    #
    return Sup_PID

##################################################

def Get_Dev_Info(hostname, Model_PID):
    modular_device = False
    #
    #Checks supplied chassis PID to determine if device is modular.
    if Model_PID in Modular_PIDs:
        modular_device = True
    #
    #If device is modular, find its supervisor PID and IOS File
    if modular_device:
        Sup_PID = Get_Sup_PID(hostname)
        IOS_file = Get_SW(hostname)
    #
    #If device isn't modular, just find its IOS file and set the supervisor PID to none.
    else:
        Sup_PID = None
        IOS_file = Get_SW(hostname)
    #
    return Sup_PID,IOS_file

##################################################

def Get_HW_SW(hostname):
    #Primary chassis PID SNMP OID
    Model_PID = SNMP_OS_Call(hostname, oid="1.3.6.1.2.1.47.1.1.1.1.13.1").split()[-1][1:-1]
    #Few checks to handle SNMP errors on devices that use alternative SNMP OIDs for chassis PID
    if Model_PID == "" or Model_PID == "MIDPLANE":
        Model_PID = SNMP_OS_Call(hostname, oid="1.3.6.1.2.1.47.1.1.1.1.13.1000").split()[-1][1:-1]
        if Model_PID == "I":
            Model_PID = SNMP_OS_Call(hostname, oid="1.3.6.1.2.1.47.1.1.1.1.13.1001").split()[-1][1:-1]
            if Model_PID == "I":
                Model_PID = SNMP_OS_Call(hostname, oid="mib-2.47.1.1.1.1.7.1").split()[-2][1:]
    elif Model_PID == "I":
        Model_PID = SNMP_OS_Call(hostname, oid="mib-2.47.1.1.1.1.13.1001").split()[-1][1:-1]
    #
    #Flag unresolved SNMP Errors while getting chassis PID
    if Model_PID in SNMP_errors:
        Model_PID = "SNMP_ERROR"
    #
    if len(Model_PID) > 8 and Model_PID in hostname:
        Model_PID = "SNMP_ERROR"
    #
    #Retrieve Supervisor PID (if device is modular) and IOS File
    Sup_PID,IOS_file = Get_Dev_Info(hostname,Model_PID)
    #
    return Model_PID,Sup_PID,IOS_file

##################################################