import openpyxl

__author__ = 'jacurran'

##################################################

def find_key(hostname,hw_pid,sup_pid):
    """
    Determine Python App Key.
    Will use this to query the Standards Excel for applicable IOS filenames.
    (Recommended, LD, Acceptable)
    """

    Maestro_key = None

    if sup_pid:
        if sup_pid in ["WS-X45-SUP8-E"]:
            Maestro_key = "WS-X45-SUP8-E"

        elif sup_pid in ["WS-X45-SUP7-E"]:
            Maestro_key = "WS-X45-SUP7-E"

        elif sup_pid in ["NPE-G1"]:
            Maestro_key = "NPE-G1"

        elif sup_pid in ["NPE-G2"]:
            Maestro_key = "NPE-G2"

        elif sup_pid in ["ASR1000-RP1",
                         "ASR1002-RP1"]:
            Maestro_key = "ASR1000-RP1"

        elif sup_pid in ["ASR1000-RP2"]:
            Maestro_key = "ASR1000-RP2"

        elif sup_pid in ["VS-SUP2T-10G"] \
                and "-wl" in hostname \
                and "-gw" in hostname:
            Maestro_key = "VS-SUP2T-10G-WLGW"

        elif sup_pid in ["VS-SUP2T-10G"]:
            Maestro_key = "VS-SUP2T-10G"

        elif sup_pid in ["WS-SUP32-GE-3B"]:
            Maestro_key = "WS-SUP32-GE-3B"

        elif sup_pid in ["WS-SUP720-3B",
                         "VS-S720-10G",
                         "WS-SUP720-3BXL"] \
                and "-wl" in hostname \
                and "-gw" in hostname:
            Maestro_key = "SUP720-WLGW"

        elif sup_pid in ["WS-SUP720-3B",
                         "VS-S720-10G",
                         "WS-SUP720-3BXL"] \
                and "-sw" in hostname:
            Maestro_key = "SUP720-SW"

        elif sup_pid in ["WS-SUP720-3B",
                         "VS-S720-10G",
                         "WS-SUP720-3BXL"] \
                and "vpn" in hostname:
            Maestro_key = "SUP720-DMVPN"

        elif sup_pid in ["WS-SUP720-3B",
                         "VS-S720-10G",
                         "WS-SUP720-3BXL"] \
                and "-gw" in hostname:
            Maestro_key = "SUP720-GW"

    elif not sup_pid:
        if hw_pid in ["C6880-X"]:
            Maestro_key = "C6880"

        elif hw_pid in ["3845",
                        "CISCO3845"]:
            Maestro_key = "CISCO3845"

        elif hw_pid in ["ISR4451-X/K9"]:
            Maestro_key = "ISR4451"

        elif hw_pid in ["IE-3010-16S-8PC"]:
            Maestro_key = "IE-3010"

        elif hw_pid in ["WS-C4500X-16",
                        "WS-C4500X-32"]:
            Maestro_key = "C4500X"

        elif hw_pid in ["WS-C4900M",
                        "WS-C4948E",
                        "WS-C4948E-F"]:
            Maestro_key = "C49XX-ME"

        elif hw_pid in ["CISCO3945-CHASSIS"] \
                and not "cvp" in hostname:
            Maestro_key = "CISCO3945"

        elif hw_pid in ["CISCO3945-CHASSIS"] \
                and "cvp" in hostname:
            Maestro_key = "CISCO3945-CVP"

        elif hw_pid in ["CISCO2901/K9"]:
            Maestro_key = "CISCO2901"

        elif hw_pid in ["CISCO2911/K9"]:
            Maestro_key = "CISCO2911"

        elif hw_pid in ["WS-C3750E-24TD-E",
                        "WS-C3750E-48PD-EF",
                        "WS-C3750E-48PD-SF",
                        "WS-C3750X-24P-S",
                        "WS-C3750X-24S-S",
                        "WS-C3750X-24T-S",
                        "WS-C3750X-24T-L",
                        "WS-C3750X-48P-L",
                        "WS-C3750X-48P-S",
                        "WS-C3750X-48T-S",
                        "WS-C3750X-48PF-E",
                        "WS-C3750X-48PF-L",
                        "WS-C3750X-48PF-S"]:
            Maestro_key = "C3750EX"

        elif hw_pid in ["WS-C3750-24PS-S",
                        "WS-C3750-48PS-S",
                        "WS-C3750G-12S-S",
                        "WS-C3750G-24PS-S",
                        "WS-C3750G-24PS-E",
                        "WS-C3750G-24TS-S1U",
                        "WS-C3750G-48PS-S",
                        "WS-C3750G-48PS-E",
                        "WS-C3750G-48TS-S"]:
            Maestro_key = "C3750-G"

        elif hw_pid in ["WS-C3560-12PC-S"]:
            Maestro_key = "WS-C3560-12PC-S"

        elif hw_pid in ["CISCO2951/K9"]:
            Maestro_key = "CISCO2951"

        elif hw_pid in ["2611XM"]:
            Maestro_key = "2611XM"

        elif hw_pid in ["CISCO2811",
                        "2811"]:
            Maestro_key = "CISCO2811"

        elif hw_pid in ["SM-ES3G-16-P",
                        "SM-ES3G-24-P"]:
            Maestro_key = "SM-ES3G"

        elif hw_pid in ["WS-C3850-48P",
                        "WS-C3850-48U"] \
                and "cl-" in hostname:
            Maestro_key = "C3850CL"

        elif hw_pid in ["WS-C3850-48P",
                        "WS-C3850-48U"]:
            Maestro_key = "C3850W"

        elif hw_pid in ["CISCO891W-AGN-A-K9",
                        "CISCO892W-AGN-E-K9"]:
            Maestro_key = "CISCO890"

        elif hw_pid in ["WS-C4948",
                        "WS-C4948-10GE"]:
            Maestro_key = "WS-C4948-XX"

    return Maestro_key

##################################################

def get_standards_info(hostname,
                       hw_pid,
                       sup_pid,
                       xldir):

    xlfile = xldir+"/Factory/IOS_Standards_NO2.xlsx"

    search_key = find_key(hostname,hw_pid,sup_pid)

    wb = openpyxl.load_workbook(xlfile)
    sheet = wb.active
    current_row = 10
    standards_tuple = ()

    Maestro_key = True
    Maestro_key_column = "A"

    recommend_IOS_file_column = "D"
    recommend_IOS_md5_column = "E"
    recommend_IOS_FPD_file_column = "L"
    recommend_IOS_FPD_md5_column = "M"

    LD_IOS_file_column = "F"
    LD_IOS_md5_column = "G"
    LD_IOS_FPD_file_column = "N"
    LD_IOS_FPD_md5_column = "O"

    acceptable_ios_file_column = "H"

    recommend_rommon_file_column = "J"
    recommend_rommon_md5_column = "K"


    while Maestro_key != "None":
        Maestro_key = str(sheet[Maestro_key_column + str(current_row)].value).strip()

        if Maestro_key ==  search_key:
            recommend_IOS_file = str(sheet[recommend_IOS_file_column + str(current_row)].value).strip()
            if recommend_IOS_file == "None":
                recommend_IOS_file = None

            recommend_IOS_md5 = str(sheet[recommend_IOS_md5_column + str(current_row)].value).strip()
            if recommend_IOS_md5 == "None":
                recommend_IOS_md5 = None

            recommend_IOS_FPD_file = str(sheet[recommend_IOS_FPD_file_column + str(current_row)].value).strip()
            if recommend_IOS_FPD_file == "None":
                recommend_IOS_FPD_file = None

            recommend_IOS_FPD_md5 = str(sheet[recommend_IOS_FPD_md5_column + str(current_row)].value).strip()
            if recommend_IOS_FPD_md5 == "None":
                recommend_IOS_FPD_md5 = None

            recommend_rommon_file = str(sheet[recommend_rommon_file_column + str(current_row)].value).strip()
            if recommend_rommon_file == "None":
                recommend_rommon_file = None

            recommend_rommon_md5 = str(sheet[recommend_rommon_md5_column + str(current_row)].value).strip()
            if recommend_rommon_md5 == "None":
                recommend_rommon_md5 = None

            LD_IOS_file = str(sheet[LD_IOS_file_column + str(current_row)].value).strip()
            if LD_IOS_file == "None":
                LD_IOS_file = None

            LD_IOS_md5 = str(sheet[LD_IOS_md5_column + str(current_row)].value).strip()
            if LD_IOS_md5 == "None":
                LD_IOS_md5 = None

            LD_IOS_FPD_file = str(sheet[LD_IOS_FPD_file_column + str(current_row)].value).strip()
            if LD_IOS_FPD_file == "None":
                LD_IOS_FPD_file = None

            LD_IOS_FPD_md5 = str(sheet[LD_IOS_FPD_md5_column + str(current_row)].value).strip()
            if LD_IOS_FPD_md5 == "None":
                LD_IOS_FPD_md5 = None

            acceptable_ios_file = str(sheet[acceptable_ios_file_column + str(current_row)].value).strip()
            if acceptable_ios_file == "None":
                acceptable_ios_file = None

            standards_tuple = (recommend_IOS_file,
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

            break
        else:
            current_row += 1

    return standards_tuple

##################################################

