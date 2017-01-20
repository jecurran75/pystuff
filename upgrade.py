from IOS_Upgrader.Maestro.Maestros import IOS_Maestro
from IOS_Upgrader.Jedi import reload_IOS

__author__ = 'jacurran'

CR = None
CR_attempts = 0
LD = False
acceptable_IOS_OK = True
result = False

hostname = raw_input("Hostname: ").lower().strip()

LD_check = raw_input("Is this device LD? (Y/N default = N): ").lower().strip()
if LD_check == "y":
    LD = True

acceptable_ok = raw_input("Is it acceptable to run acceptable IOS on this device? (Y/N default = Y): ").lower().strip()
if acceptable_ok == "n":
    acceptable_IOS_OK = False

y_or_n = raw_input("Do you have a CR? (Y/N default = N): ").lower().strip()
if y_or_n == "y":
    while CR_attempts < 3:
        print
        CR = raw_input("CR # : ").strip()
        CR = CR.upper()

        if len(CR) == 15 and "CRQ" in CR and CR_attempts < 3:
            break
        else:
            print "Invalid CR number, please check and try again."
            CR_attempts += 1
            CR = None

        if CR_attempts >= 3:
            result = "You have exceeded the maximum number of attempts to enter a valid CR number!"
            CR = None

else:
    print "\nEven though you don't have a CR, I can still analyze that hostname for compliance to IOS standards."

if CR_attempts < 3:
    result = IOS_Maestro(hostname=hostname,CR=CR,LD=LD, acceptable_IOS_OK=acceptable_IOS_OK)
    #result = reload_IOS(hostname=hostname, LD=LD)

    print
    print result
    print

#if CR:
#    answer = raw_input("Do you want to proceed with the reload utility? (Y/N default = N): ").lower()

#    if answer == "y":
#        result = IOS_bouncer(hostname=hostname,LD=LD)

#        print
#        print result
#        print

