import paramiko
import time
import cPickle as pickle
from getpass import getpass,getuser
import commands
from Get_HW_SW import sup_OID_list,SNMPv3_login,Valid_Sup_PIDs
from subprocess import call, PIPE, STDOUT

__author__ = 'jacurran'

##################################################

Stack_OID_list = ["mib-2.47.1.1.1.1.2.1001",
                  "mib-2.47.1.1.1.1.2.2001",
                  "mib-2.47.1.1.1.1.2.3001",
                  "mib-2.47.1.1.1.1.2.4001",
                  "mib-2.47.1.1.1.1.2.5001",
                  "1.3.6.1.2.1.47.1.1.1.1.13.2",
                  "1.3.6.1.2.1.47.1.1.1.1.13.3",
                  "1.3.6.1.2.1.47.1.1.1.1.13.4",
                  "1.3.6.1.2.1.47.1.1.1.1.13.5",
                  "1.3.6.1.2.1.47.1.1.1.1.13.6"]

##################################################

class IOS_NetDev:
    """ Generic Network Device """

    # This allows for the submission of all possible attribute values.
    # Most device types represented by the child classes won't need them all.
    # Child classes will only forward the relevant ones here.
    # Non-relevant attributes will receive their default values.
    def __init__(self, name,
                 HW_PID="",
                 Sup_PID="",
                 current_IOS_file="",
                 new_IOS_file="",
                 IOS_md5_hash="",
                 new_FPD_file="",
                 FPD_md5_hash="",
                 ROMMON_file="",
                 ROMMON_md5_hash=""):

        self.simulation = False

        self.name = name
        self.loggedin = False

        self.media_list = ["flash:"]
        self.removable_flash_list = []

        self.prime_boot_loc = "flash:"
        self.sec_boot_loc = None
        self.boot_statement_prefix = "boot system "
        self.single_boot_statement = False

        self.new_IOS_file = new_IOS_file
        self.IOS_md5_hash = IOS_md5_hash
        self.new_FPD_file = new_FPD_file
        self.FPD_md5_hash = FPD_md5_hash
        self.ROMMON_file = ROMMON_file
        self.ROMMON_md5_hash = ROMMON_md5_hash

        self.current_IOS_file = current_IOS_file
        self.primary_copy_location = None
        self.available_media = []
        self.prompt = None
        self.stack_size = 0
        self.Sup_num = 0
        self.sup_OID_list = sup_OID_list
        self.HW_PID = HW_PID
        self.Sup_PID = Sup_PID
        self.enable_mode = True

        self.accessible_console_list = []
        self.misconfigured_console_list = []
        self.dead_console_list = []
        self.incompatible_console_list = []

        self.distance = -1
        self.reload_cmd_list = ["reload"]
        self.SSH_HUNG = False
        self.slice_points=(0,0)
        self.ROMMON_search_value = "THIS_WILL_BE_REPLACED_AT_CHILD_CLASS_LEVEL"

        self.Non_Sup_ROMMON_OID = "1.3.6.1.2.1.47.1.1.1.1.9.1000"
        self.file_ver = ""
        self.rommon_ver_list = []

    def SNMP_OS_Call(self, oid):
        OS_Call = commands.getoutput(
            '/usr/bin/snmpbulkwalk -v3 -l authNopriv -u {} -a SHA -A {} {} {}'
                .format(SNMPv3_login[0],SNMPv3_login[1],self.name,oid))
        return OS_Call

    def SNMPv3_config(self):
        if self.loggedin:
            self.sendcmd("config term")
            self.sendcmd("snmp-server group network-v3group v3 auth"
                         " read novacm write novacm access 90")
            self.sendcmd("snmp-server user network-v3user network-v3group v3 auth "
                         "md5 DmZ3nLik34mor priv des56 tHr33m0Re4mor")
            self.sendcmd("snmp-server user network-v3user network-v3group v3 auth "
                         "sha D0ntPr1nT4mor priv des56 tHr33m0Re4mor ")
            self.sendcmd("snmp-server user network-v3user network-v3group v3 auth sha"
                         " D0ntPr1nT4mor priv aes 128 L1v3!0Ng3r4mor")
            self.sendcmd("end")
            self.sendcmd("copy run start")


    def get_stack_num(self):
        stack_num = 0
        if "3750" in self.HW_PID:
            for OID in Stack_OID_list:
                result = self.SNMP_OS_Call(OID).split()[-1][1:-1]
                if "3750" in result:
                    stack_num += 1
            self.stack_size = stack_num
        elif "C3850" in self.HW_PID:
            for OID in Stack_OID_list:
                result = self.SNMP_OS_Call(OID)
                if "C3850" in result:
                     stack_num += 1
            self.stack_size = stack_num

    def get_sup_num(self):
        for OID in sup_OID_list:
            result = self.SNMP_OS_Call(OID)
            if self.Sup_PID in result:
                self.Sup_num += 1

    def login(self, quiet=False):
        if not self.loggedin:
            username, password = get_login(file="./pylogin.dat")
            if username == None and password == None:
                set_login()
                username, password = get_login(file="./pylogin.dat")

            username_cec, password_cec = get_login(file="./pylogin_cec.dat")
            if username_cec == None and password_cec == None:
                set_login_cec()
                username_cec, password_cec = get_login(file="./pylogin_cec.dat")

            # Create instance of SSHClient object
            self.ssh = paramiko.SSHClient()

            # Automatically add untrusted hosts (make sure okay for security policy in your environment)
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # initiate SSH connection
            self.ssh.connect(self.name, username=username, password=password, look_for_keys=False, allow_agent=False)

            # Use invoke_shell to establish an 'interactive session'
            self.remote_conn = self.ssh.invoke_shell()
            time.sleep(2)

            self.CS_menu_check()

            self.sendcmd("terminal length 0\n", buff=100000)

            if not quiet:
                print "Login to %s successful." % self.name
            self.loggedin = True
        else:
            print "You are already logged into %s." % self.name

    def logout(self, quiet=False):
        if self.loggedin:
            self.ssh.close()
            self.loggedin = False
            if not quiet:
                print "Successfully logged out of %s." % self.name
        else:
            print "You are not logged into %s." % self.name

    def sendcmd(self, command, sleep=1, buff=100000):
        # Now let's try to send the router a command
        self.SSH_HUNG = False
        if not self.SSH_HUNG:
            self.remote_conn.send(command + "\n")
            # Wait for the command to complete
            time.sleep(sleep)

            if not self.remote_conn.recv_ready():
                time.sleep(5)
                if not self.remote_conn.recv_ready():
                    self.SSH_HUNG = True

        if not self.SSH_HUNG:
            self.output = self.remote_conn.recv(buff).split("\r\n")

            while True:
                try:
                    index = self.output.index('')
                    del self.output[index]
                except:
                    break

        elif self.SSH_HUNG:
            self.output = ["PARAMIKO INCOMPATIBILITY ERROR"]

        return self.output

    def get_prompt(self):
        if self.loggedin:
            self.prompt = self.sendcmd("")[0].strip()
            self.prompt = self.sendcmd("")[0].strip()
            self.prompt = self.sendcmd("")[0].strip()

    def CS_menu_check(self):
        prompt = self.sendcmd("")[0].strip()
        del prompt
        prompt = self.sendcmd("")[0].strip()
        if prompt in ["Selection:"]:
            self.sendcmd("x")

    def determine_media(self):
        if self.loggedin and self.media_list:
            available_media = self.media_list[:]
            for location in self.removable_flash_list:
                result = self.sendcmd("dir {}".format(location))
                for line in result:
                    if "bytes" in line:
                        available_media.append(location)
            primary_copy_location = available_media.pop(0)
            self.available_media = available_media
            self.primary_copy_location = primary_copy_location

    def new_file_there(self, location, the_file):
        if self.loggedin:
            file_there = False
            result = self.sendcmd("dir {}".format(location))
            for line in result:
                if the_file in line:
                    file_there = True
            if file_there:
                return True
            else:
                return False

    def valid_md5(self,location,the_file,md5_hash):
        if self.loggedin:
            md5_calc_done = False
            valid_md5 = False
            result = self.sendcmd("verify /md5 {}/{}".format(location, the_file), sleep=10)
            while not md5_calc_done:
                result2 = self.sendcmd("")
                result.extend(result2)
                for line in result:
                    if "Done!" in line:
                        md5_calc_done = True
                    if md5_hash in line:
                        valid_md5 = True
                        md5_calc_done = True
            if valid_md5:
                return True
            else:
                return False
        else:
            return False

    def del_new_file(self, location, the_file=""):
        if not the_file:
            the_file = self.new_IOS_file
        if self.loggedin:
            result = self.sendcmd("del {}{}".format(location, the_file))
            del result
            result = self.sendcmd("")
            del result
            result = self.sendcmd("")
            del result
            result = self.sendcmd("")
            del result

    def IOS_reclaim_space(self,location):
        if self.loggedin:
            result = self.sendcmd("dir {}".format(location))
            file_list = [line.split()[-1] for line in result]
            file_list = file_list[:-2]

            for file in file_list:
                if file != self.new_IOS_file \
                        and file != self.current_IOS_file \
                        and ".bin" in file:
                    if self.simulation:
                        print "{}{} will be deleted".format(location, file)
                    elif not self.simulation:
                        self.sendcmd("del {}{}".format(location,file))
                        self.sendcmd("")
                        self.sendcmd("")

    def fpd_reclaim_space(self,location):
        self.reclaim_space(location=location, search_term="fpd")

    def ROMMON_reclaim_space(self, location):
        self.reclaim_space(location=location,search_term=self.ROMMON_search_value)

    def reclaim_space(self, location, search_term):
        if self.loggedin:
            result = self.sendcmd("dir {}".format(location))
            file_list = [line.split()[-1] for line in result]
            file_list = file_list[:-2]

            for file in file_list:
                if search_term in file:
                    if self.simulation:
                        print "{}{} will be deleted".format(location, file)
                    elif not self.simulation:
                        self.sendcmd("del {}{}".format(location,file))
                        self.sendcmd("")
                        self.sendcmd("")

    def prompt_back(self):
        if self.loggedin and self.prompt:
            result = self.sendcmd("")
            if result:
                if result[0].strip() == self.prompt:
                    return True
                else:
                    return False
            else:
                return False

    def scp_copy_file(self, source, destination, the_file):
        # Needed to build copy command for SCP syntax.
        username_cec, password_cec = get_login(file="./pylogin_cec.dat")

        copy_command = "copy scp://{}:{}@{}/{} {}".format(username_cec, password_cec, source, the_file, destination)
        # Use the copy_file method and return True/False to signify if there was an error.
        copy_error = self.copy_file(destination, the_file, copy_command)
        return copy_error

    def ftp_copy_file(self, source, destination, the_file):
        # Converts ENS server file structure from SCP syntax to FTP syntax.
        source_server = source.split(":")[0]
        source_dir = source.split(":")
        if source_dir[-1] == "":
            source_dir = source_dir[:-1]
        source_dir = source_dir[-1].split("/")[-1]
        source = "{}/{}".format(source_server,source_dir)

        copy_command = "copy ftp://{}/{} {}".format(source, the_file, destination)
        # Use the copy_file method and return True/False to signify if there was an error.
        copy_error = self.copy_file(destination, the_file, copy_command)
        return copy_error

    def local_copy_file(self, source, destination, the_file):
        copy_command = "copy {}{} {}".format(source, the_file, destination)
        # Use the copy_file method and return True/False to signify if there was an error.
        copy_error = self.copy_file(destination, the_file, copy_command)
        return copy_error

    def copy_file(self, destination, the_file, copy_command):
        prompt_back_yet = False
        access_issue = False

        if self.loggedin:
            if not self.prompt:
                self.get_prompt()

            self.sendcmd(copy_command)
            self.sendcmd("")
            self.sendcmd("")
            time.sleep(5)

            if self.prompt_back():
                if not self.new_file_there(location=destination,the_file=the_file):
                    access_issue = True

            while not access_issue and not prompt_back_yet:
                time.sleep(5)
                prompt_back_yet = self.prompt_back()

            if access_issue:
                return True
            elif not self.new_file_there(location=destination,the_file=the_file):
                return True
            else:
                return False

    def backup_run_config(self, location=None):
        if not location:
            location = self.prime_boot_loc
        if self.loggedin:
            result = self.sendcmd("copy running-config {}".format(location))
            del result
            result = self.sendcmd("running-config")
            del result
            result = self.sendcmd("",sleep=3)
            del result
            result = self.sendcmd("")
            del result

    def get_boot_var_deletes(self):
        if self.loggedin:
            boot_vars = self.sendcmd("show run | i boot system",sleep=5)[1:-1]
            deletions = ["no "+boot_var for boot_var in boot_vars]
            return deletions

    def get_new_boot_vars(self):
        boot_statement_list = []

        if not self.single_boot_statement:
            boot_statement_list.append(self.boot_statement_prefix + self.prime_boot_loc + self.new_IOS_file)
            if self.sec_boot_loc:
                boot_statement_list.append(self.boot_statement_prefix + self.sec_boot_loc + self.new_IOS_file)

            boot_statement_list.append(self.boot_statement_prefix + self.prime_boot_loc + self.current_IOS_file)
            if self.sec_boot_loc:
                boot_statement_list.append(self.boot_statement_prefix + self.sec_boot_loc + self.current_IOS_file)

        elif self.single_boot_statement:
            boot_statement_list.append(self.boot_statement_prefix + self.prime_boot_loc + self.new_IOS_file)

        return boot_statement_list

    def change_boot_vars(self):
        if self.loggedin:
            commands = ["config terminal"]
            commands.extend(self.get_boot_var_deletes())
            commands.extend(self.get_new_boot_vars())
            commands.append("config-register 0x2102")
            commands.append("end")
            commands.append("copy run start")
            for line in commands:
                if not self.simulation:
                    self.sendcmd(line,sleep=2)
                elif self.simulation:
                    print line
            self.sleep = 5

    def sys_prepare_ROMMON(self):
        if self.loggedin:
            commands = ["config terminal"]
            commands.extend(self.get_boot_var_deletes())
            commands.append(self.boot_statement_prefix + self.prime_boot_loc + self.ROMMON_file)
            if self.sec_boot_loc:
                commands.append(self.boot_statement_prefix + self.sec_boot_loc + self.ROMMON_file)
            commands.append(self.boot_statement_prefix + self.prime_boot_loc + self.current_IOS_file)
            if self.sec_boot_loc:
                commands.append(self.boot_statement_prefix + self.sec_boot_loc + self.current_IOS_file)
            commands.append("config-register 0x0102")
            commands.append("end")
            commands.append("copy run start")
            for line in commands:
                if not self.simulation:
                    self.sendcmd(line,sleep=2)
                elif self.simulation:
                    print line
            self.sleep = 5

    def get_distance(self):
        """
        This function determines how many hops away from the Linux server a device sits.
        This is important to get a network depth model so the furthest network layer can be reloaded first.
        """

        distance = len(commands.getoutput("traceroute {}".format(self.name)).split("\n")[1:])
        if distance >= 30:
            self.distance = 0
        else:
            self.distance = distance

    def reload(self):
        if self.loggedin:
            if not self.prompt:
                self.get_prompt()
            self.sendcmd("copy run start")
            self.sendcmd("",sleep=5)
            self.sendcmd("")

            prompt_back_yet = False
            while not not prompt_back_yet:
                time.sleep(5)
                prompt_back_yet = self.prompt_back()

            try:
                for cmd in self.reload_cmd_list:
                    self.sendcmd(cmd,sleep=2)
                    self.sendcmd("")
                    self.sendcmd("")
            except:
                return "{} is reloading.\nPlease confirm it comes back online with your monitoring system."\
                    .format(self.name)
            else:
                return "{} is reloading.\nPlease confirm it comes back online with your monitoring system." \
                    .format(self.name)

    def is_alive(self, destination=None):
        if not destination:
            destination = self.name
        args = ("ping -c 1 " + destination).split()
        if call(args, stdout=PIPE, stderr=STDOUT) == 0:
            return True
        elif call(args, stdout=PIPE, stderr=STDOUT) == 0:
            return True
        else:
            return False

    def file_upload(self,new_file,
                    md5_hash_provided,
                    file_source="ens-sj1.cisco.com://users/ftp/images"):

        if self.new_file_there(the_file=new_file,
                                 location=self.primary_copy_location):
            if md5_hash_provided:
                if not self.valid_md5(the_file=new_file,
                                        md5_hash=md5_hash_provided,
                                        location=self.primary_copy_location):
                    self.del_new_file(the_file=new_file,
                                        location=self.primary_copy_location)

        if not self.new_file_there(the_file=new_file,
                                     location=self.primary_copy_location):

            self.ftp_copy_file(source=file_source,
                                 destination=self.primary_copy_location,
                                 the_file=new_file)

            if self.new_file_there(the_file=new_file,
                                     location=self.primary_copy_location):
                if md5_hash_provided:
                    if not self.valid_md5(the_file=new_file,
                                            md5_hash=md5_hash_provided,
                                            location=self.primary_copy_location):
                        self.del_new_file(the_file=new_file,
                                            location=self.primary_copy_location)

        copy_attempt = 0
        while not self.new_file_there(the_file=new_file,
                                        location=self.primary_copy_location
                                        ) and copy_attempt < 3:

            self.scp_copy_file(source=file_source,
                                 destination=self.primary_copy_location,
                                 the_file=new_file)

            if self.new_file_there(the_file=new_file,
                                     location=self.primary_copy_location):
                if md5_hash_provided:
                    if not self.valid_md5(the_file=new_file,
                                            md5_hash=md5_hash_provided,
                                            location=self.primary_copy_location):
                        self.del_new_file(the_file=new_file,
                                            location=self.primary_copy_location)
            copy_attempt += 1

        if not self.new_file_there(the_file=new_file,
                                     location=self.primary_copy_location):
            return True  # Yes there was a problem copying the file from the server to the device.
        else:
            for location in self.available_media:
                if not self.new_file_there(location=location,
                                             the_file=new_file):
                    self.local_copy_file(source=self.primary_copy_location,
                                           destination=location,
                                           the_file=new_file)
            return False  # No error copying the file from the server to the device.

    def ver_extractor(self, raw_syntax, slice_points=(0, 0)):
        stripped_version = ""
        #
        slice_start = slice_points[0]
        slice_end = slice_points[1]
        if slice_end == 0:
            rough_ver = raw_syntax[slice_start:]
        else:
            rough_ver = raw_syntax[slice_start:slice_end]

        num_hold = ""
        alpha_hold = ""
        hold_list = []

        for char in rough_ver:
            if char.isdigit():
                num_hold += char
                if alpha_hold:
                    hold_list.append(alpha_hold)
                    alpha_hold = ""
            elif char.isalpha():
                alpha_hold += char
                if num_hold:
                    hold_list.append(num_hold)
                    num_hold = ""

        if num_hold:
            hold_list.append(num_hold)

        if alpha_hold:
            hold_list.append(alpha_hold)

        stripped_version = "-".join(hold_list)

        return stripped_version

    def Get_ROMMON_SNMP(self):
        # Tries to get a known valid supervisor PID using a list of possible SNMP OID values.
        #
        self.rommon_ver_list = []
        if self.Sup_PID:
            for Sup_OID in sup_OID_list:
                # Get the supervisor PID via SNMP
                Sup_PID = self.SNMP_OS_Call(oid=Sup_OID).split()[-1][1:-1]
                #
                # Checks against a valid results list, stops search once one is found.
                if Sup_PID in Valid_Sup_PIDs:
                    # Determine corresponding ROMMON OID from identified Sup OID
                    disassembled_OID = Sup_OID.split(".")
                    disassembled_OID[-2] = "9"
                    ROMMON_OID = ".".join(disassembled_OID)
                    #
                    ROMMON_ver = self.ver_extractor(raw_syntax=self.SNMP_OS_Call(oid=ROMMON_OID).split()[-1][1:-1])
                    self.rommon_ver_list.append(ROMMON_ver)
        else:
            ROMMON_ver = self.ver_extractor(raw_syntax=self.SNMP_OS_Call(oid=self.Non_Sup_ROMMON_OID).split()[-1][1:-1])
            self.rommon_ver_list.append(ROMMON_ver)

    def ROMMON_Compare(self):
        ROMMON_valid = True

        self.Get_ROMMON_SNMP()
        self.file_ver = self.ver_extractor(raw_syntax=self.ROMMON_file, slice_points=self.slice_points)

        for rommon_ver in self.rommon_ver_list:
            file_ver_temp_list = self.file_ver.split("-")[:]
            rommon_ver_temp_list = rommon_ver.split("-")[:]

            if len(rommon_ver_temp_list) >= len(file_ver_temp_list) and ROMMON_valid:
                for index in range(len(file_ver_temp_list)):
                    if rommon_ver_temp_list[index].isdigit() and file_ver_temp_list[index].isdigit():
                        rommon_ver_temp_list[index] = int(rommon_ver_temp_list[index])
                        file_ver_temp_list[index] = int(file_ver_temp_list[index])
                    if rommon_ver_temp_list[index] < file_ver_temp_list[index]:
                        ROMMON_valid = False
                        break
                    elif rommon_ver_temp_list[index] > file_ver_temp_list[index]:
                        break

            elif ROMMON_valid:
                for index in range(len(rommon_ver_temp_list)):
                    if rommon_ver_temp_list[index].isdigit() and file_ver_temp_list[index].isdigit():
                        rommon_ver_temp_list[index] = int(rommon_ver_temp_list[index])
                        file_ver_temp_list[index] = int(file_ver_temp_list[index])
                    if rommon_ver_temp_list[index] < file_ver_temp_list[index]:
                        ROMMON_valid = False
                        break
                    elif rommon_ver_temp_list[index] > file_ver_temp_list[index]:
                        break

        return ROMMON_valid

##################################################

def set_login():
    username = getuser()+".web"
    username = raw_input("Dot Web Username '%s':" % username)
    if not username:
        username = getuser()+".web"
    password = getpass("DOT Web Password: ")
    f = open("./pylogin.dat","wb")
    pickle.dump(username,f)
    pickle.dump(password,f)
    f.close()

##################################################

def set_login_cec():
    username = getuser()
    username = raw_input("CEC Username '%s':" % username)
    if not username:
        username = getuser()
    password = getpass("CEC Password: ")
    f = open("./pylogin_cec.dat","wb")
    pickle.dump(username,f)
    pickle.dump(password,f)
    f.close()

##################################################

def get_login(file):
    try:
        f = open(file,"rb")
        username = pickle.load(f)
        password = pickle.load(f)
        f.close()
    except:
        print "Login Credentials not set."
        return None,None
    else:
        return username,password

##################################################

class Group1(IOS_NetDev):
    """ Class base Template for:
    Cisco 4500X
    Cisco Cat4948-10GE family
    Cisco Cat4900M"""

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash, ROMMON_file, ROMMON_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            ROMMON_file=ROMMON_file,
                            ROMMON_md5_hash=ROMMON_md5_hash)

        self.media_list = ["bootflash:"]
        self.removable_flash_list = ["slot0:"]
        self.prime_boot_loc = "bootflash:"
        self.sec_boot_loc = "slot0:"
        self.boot_statement_prefix = "boot system flash "
        self.slice_points = (26, 0)

        self.ROMMON_search_value = "promupgrade"

##################################################

class C6500S2T(IOS_NetDev):
    """ Class tailored for Cat6500/Cat7600/6807 family with Sup 2T """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, Sup_PID, current_IOS_file, new_IOS_file, IOS_md5_hash,
                 new_FPD_file, FPD_md5_hash):
        IOS_NetDev.__init__(self, name,
                            Sup_PID=Sup_PID,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            new_FPD_file=new_FPD_file,
                            FPD_md5_hash=FPD_md5_hash)

        self.prime_boot_loc = "bootdisk:"
        self.sec_boot_loc = "disk0:"
        self.boot_statement_prefix = "boot system flash "

        self.get_sup_num()
        if self.Sup_num == 2:
            self.media_list = ["bootdisk:","slavebootdisk:"]
            self.removable_flash_list = ["disk0:","slavedisk0:"]
        elif self.Sup_num == 1:
            self.media_list = ["bootdisk:"]
            self.removable_flash_list = ["disk0:"]

##################################################

class C6500(IOS_NetDev):
    """ Class tailored for Cat6500/Cat7600/6807 family with Sup 720 and Sup32 """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, Sup_PID, current_IOS_file, new_IOS_file, IOS_md5_hash,
                 new_FPD_file, FPD_md5_hash):
        IOS_NetDev.__init__(self, name,
                            Sup_PID=Sup_PID,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            new_FPD_file=new_FPD_file,
                            FPD_md5_hash=FPD_md5_hash)

        self.prime_boot_loc = "sup-bootdisk:"
        self.sec_boot_loc = "disk0:"
        self.boot_statement_prefix = "boot system flash "

        self.get_sup_num()
        if self.Sup_num == 2:
            self.media_list = ["sup-bootdisk:","slavesup-bootdisk:"]
            self.removable_flash_list = ["disk0:","slavedisk0:"]
        elif self.Sup_num == 1:
            self.media_list = ["sup-bootdisk:"]
            self.removable_flash_list = ["disk0:"]

##################################################

class C4500(IOS_NetDev):
    """ Class tailored for Cat4500 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, Sup_PID, current_IOS_file, new_IOS_file, IOS_md5_hash, ROMMON_file, ROMMON_md5_hash):
        IOS_NetDev.__init__(self, name,
                            Sup_PID=Sup_PID,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            ROMMON_file=ROMMON_file,
                            ROMMON_md5_hash=ROMMON_md5_hash)

        self.prime_boot_loc = "bootflash:"
        self.sec_boot_loc = "slot0:"
        self.boot_statement_prefix = "boot system flash "
        self.reload_cmd_list = ["redundancy reload shelf"]
        self.slice_points = (26,0)

        self.ROMMON_search_value = "promupgrade"

        self.get_sup_num()
        if self.Sup_num == 2:
            self.media_list = ["bootflash:","slavebootflash:"]
            self.removable_flash_list = ["slot0:","slaveslot0:"]
        elif self.Sup_num == 1:
            self.media_list = ["bootflash:"]
            self.removable_flash_list = ["slot0:"]

##################################################

class C3750(IOS_NetDev):
    """ Class tailored for Cat3750 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, HW_PID, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            HW_PID=HW_PID,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

        self.media_list = []
        self.boot_statement_prefix = "boot system switch all "
        self.single_boot_statement = True

        self.get_stack_num()
        for device in range(self.stack_size):
            media = "flash{}:".format(device+1)
            self.media_list.append(media)

##################################################

class C3850(IOS_NetDev):
    """ Class tailored for Cat3850 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, HW_PID, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            HW_PID=HW_PID,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

        self.boot_statement_prefix = "boot system switch all "

        self.get_stack_num()
        if self.stack_size > 1:
            self.media_list = []
            for device in range(self.stack_size):
                media = "flash-{}:".format(device+1)
                self.media_list.append(media)

##################################################

class ASR1000(IOS_NetDev):
    """ Class tailored for Cisco ASR1000 family"""

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash, ROMMON_file, ROMMON_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            ROMMON_file=ROMMON_file,
                            ROMMON_md5_hash=ROMMON_md5_hash)

        self.media_list = ["bootflash:"]
        self.prime_boot_loc = "bootflash:"
        self.boot_statement_prefix = "boot system flash "
        self.slice_points = (15,-4)

        self.ROMMON_search_value = "rommon"

    def sys_prepare_ROMMON(self):
        if self.loggedin:
            self.get_prompt()
            commands = ["upgrade rom-monitor filename {}{} all".format(self.prime_boot_loc,self.ROMMON_file)]
            for line in commands:
                if not self.simulation:
                    self.sendcmd(line,sleep=2)
                elif self.simulation:
                    print line

            if not self.simulation:
                time.sleep(10)
                prompt_back_yet = False
                while not prompt_back_yet:
                    time.sleep(5)
                    prompt_back_yet = self.prompt_back()

##################################################

class ISR4450(IOS_NetDev):
    """ Class tailored for Cisco ISR4450 family"""

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

        self.media_list = ["bootflash:"]
        self.prime_boot_loc = "bootflash:"
        self.boot_statement_prefix = "boot system flash "

##################################################

class C4948(IOS_NetDev):
    """ Class tailored for Cisco Cat4948 family (Non 10GE)"""

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash, ROMMON_file, ROMMON_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            ROMMON_file=ROMMON_file,
                            ROMMON_md5_hash=ROMMON_md5_hash)

        self.media_list = ["bootflash:"]
        self.prime_boot_loc = "bootflash:"
        self.boot_statement_prefix = "boot system flash "
        self.slice_points = (26,0)

        self.ROMMON_search_value = "promupgrade"

##################################################

class C4948_10GE(Group1):
    """ Class tailored for Cisco Cat4948-10GE family"""

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash, ROMMON_file, ROMMON_md5_hash):
        Group1.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            ROMMON_file=ROMMON_file,
                            ROMMON_md5_hash=ROMMON_md5_hash)

        self.slice_points = (24, 0)

    def IOS_reclaim_space(self,location):
        IOS_NetDev.IOS_reclaim_space(self,location=location)
        if self.loggedin:
            self.get_prompt()
            if not self.simulation:
                if not self.prompt:
                    self.get_prompt()
                self.sendcmd("squeeze /quiet {}".format(location))
                self.sendcmd("")
                self.sendcmd("")

                prompt_back_yet = False
                while not prompt_back_yet:
                    time.sleep(5)
                    prompt_back_yet = self.prompt_back()

##################################################

class C2600(IOS_NetDev):
    """ Class tailored for Cisco 2600 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

    def IOS_reclaim_space(self,location):
        IOS_NetDev.IOS_reclaim_space(self,location=location)
        if self.loggedin:
            self.get_prompt()
            if not self.simulation:
                if not self.prompt:
                    self.get_prompt()
                self.sendcmd("squeeze /quiet {}".format(location))
                self.sendcmd("")
                self.sendcmd("")

                prompt_back_yet = False
                while not prompt_back_yet:
                    time.sleep(5)
                    prompt_back_yet = self.prompt_back()

##################################################

class C4500X(Group1):
    """ Class tailored for Cisco 4500X Family"""

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash, ROMMON_file, ROMMON_md5_hash):
        Group1.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            ROMMON_file=ROMMON_file,
                            ROMMON_md5_hash=ROMMON_md5_hash)

##################################################

class C4900M(Group1):
    """ Class tailored for Cisco Cat4900M"""

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash, ROMMON_file, ROMMON_md5_hash):
        Group1.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            ROMMON_file=ROMMON_file,
                            ROMMON_md5_hash=ROMMON_md5_hash)

##################################################

class C7200(IOS_NetDev):
    """ Class tailored for Cisco 7200 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash,
                 new_FPD_file, FPD_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash,
                            new_FPD_file=new_FPD_file,
                            FPD_md5_hash=FPD_md5_hash)

        self.media_list = ["disk2:"]
        self.prime_boot_loc = "disk2:"
        self.boot_statement_prefix = "boot system flash "

##################################################

class C6880(IOS_NetDev):
    """ Class tailored for Cisco 6880 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

        self.media_list = ["bootdisk:"]
        self.prime_boot_loc = "bootdisk:"

##################################################

class C3725(IOS_NetDev):
    """ Class tailored for Cisco 3725 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

        self.removable_flash_list = ["slot0:"]

##################################################

class C3560(IOS_NetDev):
    """ Class tailored for Cisco 3560 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self, name, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

        self.single_boot_statement = True

##################################################

class C890(IOS_NetDev):
    """ Class tailored for Cisco 3560 family """

    # Child classes will only receive relevant attributes from Sales_Order.py.
    # Only these relevant values will be forwarded to the parent class constructor.
    # Non-relevant attributes will get their default value of "" and won't be referenced further.
    def __init__(self,
                 name, current_IOS_file, new_IOS_file, IOS_md5_hash):
        IOS_NetDev.__init__(self, name,
                            current_IOS_file=current_IOS_file,
                            new_IOS_file=new_IOS_file,
                            IOS_md5_hash=IOS_md5_hash)

        self.boot_statement_prefix = "boot system flash "

##################################################

