from Inventory import *

__author__ = 'jacurran'

##################################################

#Takes in a full list of specification values.
#Only relevant ones for a given hardware platform
#will be forwarded to the target class constructor.
def specs(name,
          HW_PID="",
          Sup_PID="",
          current_IOS_file="",
          new_IOS_file="",
          IOS_md5_hash="",
          new_FPD_file="",
          FPD_md5_hash="",
          ROMMON_file="",
          ROMMON_md5_hash=""):

    if "-con" in name:
        return IOS_NetDev(name=name)

    elif Sup_PID:
        if Sup_PID in ['VS-SUP2T-10G']:
            return C6500S2T(name=name,
                            Sup_PID=Sup_PID,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            new_FPD_file=new_FPD_file,
                            FPD_md5_hash=FPD_md5_hash)

        elif Sup_PID in ['WS-SUP720-3B',
                         'VS-S720-10G',
                         'WS-SUP720-3BXL',
                         'WS-SUP32-GE-3B']:

            return C6500(name=name,
                         Sup_PID=Sup_PID,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash,
                         new_FPD_file=new_FPD_file,
                         FPD_md5_hash=FPD_md5_hash)

        elif Sup_PID in ['WS-X45-SUP8-E',
                         'WS-X45-SUP7-E']:

            return C4500(name=name,
                         Sup_PID=Sup_PID,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash,
                         ROMMON_file=ROMMON_file,
                         ROMMON_md5_hash=ROMMON_md5_hash)

        elif Sup_PID in ['NPE-G1',
                         'NPE-G2']:

            return C7200(name=name,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash,
                         new_FPD_file=new_FPD_file,
                         FPD_md5_hash=FPD_md5_hash)

        elif Sup_PID in ['ASR1000-RP1',
                         'ASR1000-RP2',
                         'ASR1002-RP1']:

            return ASR1000(name=name,
                           current_IOS_file=current_IOS_file,
                           new_IOS_file=new_IOS_file,
                           IOS_md5_hash=IOS_md5_hash,
                           ROMMON_file=ROMMON_file,
                           ROMMON_md5_hash=ROMMON_md5_hash)

    elif not Sup_PID:
        if "WS-C3750" in HW_PID:
            return C3750(name=name,
                         HW_PID=HW_PID,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash)

        elif "WS-C3850" in HW_PID:
            return C3850(name=name,
                         HW_PID=HW_PID,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash)

        elif HW_PID in ['2611',
                        '2611XM']:

            return C2600(name=name,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash)

        elif HW_PID in ['C6880-X']:
            return C6880(name=name,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash)

        elif HW_PID in ['WS-C4948E',
                        'WS-C4948',
                        'WS-C4948E-F']:

            return C4948(name=name,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash,
                         ROMMON_file=ROMMON_file,
                         ROMMON_md5_hash=ROMMON_md5_hash)

        elif HW_PID in ['ISR4451-X/K9']:
            return ISR4450(name=name,
                           current_IOS_file=current_IOS_file,
                           new_IOS_file=new_IOS_file,
                           IOS_md5_hash=IOS_md5_hash)

        elif HW_PID in ['WS-C4948-10GE']:

            return C4948_10GE(name=name,
                              current_IOS_file=current_IOS_file,
                              new_IOS_file=new_IOS_file,
                              IOS_md5_hash=IOS_md5_hash,
                              ROMMON_file=ROMMON_file,
                              ROMMON_md5_hash=ROMMON_md5_hash)

        elif HW_PID in ['WS-C4500X-16',
                        'WS-C4500X-32']:

            return C4500X(name=name,
                          current_IOS_file=current_IOS_file,
                          new_IOS_file=new_IOS_file,
                          IOS_md5_hash=IOS_md5_hash,
                          ROMMON_file=ROMMON_file,
                          ROMMON_md5_hash=ROMMON_md5_hash)

        elif HW_PID in ['WS-C4900M']:

            return C4900M(name=name,
                          current_IOS_file=current_IOS_file,
                          new_IOS_file=new_IOS_file,
                          IOS_md5_hash=IOS_md5_hash,
                          ROMMON_file=ROMMON_file,
                          ROMMON_md5_hash=ROMMON_md5_hash)

        elif HW_PID in ['3725']:
            return C3725(name=name,
                         current_IOS_file=current_IOS_file,
                         new_IOS_file=new_IOS_file,
                         IOS_md5_hash=IOS_md5_hash)

        else:
            return IOS_NetDev(name=name,
                              current_IOS_file=current_IOS_file,
                              new_IOS_file=new_IOS_file,
                              IOS_md5_hash=IOS_md5_hash)


