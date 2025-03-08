import subprocess
import shlex
from anmr_common import *

# use socat?
#USE_SERIAL_PIPE = True
USE_SERIAL_PIPE = False

#external helper programs:
SOCAT='/usr/bin/socat'
SOX_EXEC='/usr/bin/sox'
AVRDUDE='/usr/share/arduino/hardware/tools/avrdude'
AVRDUDE_CONF='/usr/share/arduino/hardware/tools/avrdude.conf'
IMAGE_VIEWER = "/usr/bin/eom -n"
KILLALL = "/usr/bin/killall"

#Anmr installs:
#this is also in Shim.py
ICON_PATH='/usr/local/share/Anmr/Icons'

#our firmware
#ARDUINO_CODE = '/usr/local/share/Anmr/arduinoCode'
FIRMWARE='/usr/local/share/Anmr/arduinoCode/arduinoCode.hex'

#pulse programs:
PROG_DIR = '/usr/local/share/Anmr/PulsePrograms'

#pulse program header file:
HEADER_NAME = 'defaults.include'

#hardware config
#these will force us to guess - if ttyACM0 exists, we'll assume uno
#if not, we'll try ttyUSB0 and assume deumillanove (atmega328) 
ARDUINO_DEV = 'auto'
ARDUINO_BOARD = 'auto'

################ End of configuration variables. TMPDIR is in anmr_common

#To force DEV and BOARD settings: 
#ARDUINO_DEV is something like: /dev/ttyUSB0 or /dev/ttyACM0
#ARDUINO_BOARD is used by scons -> avrdude to program it. 'uno' or 'atmega328'

###### for Deumillanove
#ARDUINO_DEV = '/dev/ttyUSB0'
#ARDUINO_BOARD = 'atmega328'

###### for Uno:
#ARDUINO_DEV = '/dev/ttyACM0'
#ARDUINO_BOARD = 'uno'

# the linux cdc-acm module needed for the arduino uno has a nasty habit of resetting the
# uno on every open of the file descriptor. To avoid it, we call socat to
# pipe the arduino to a pty, and then we talk to the pty.
PTY_FILE="anmr-pty"

ICON_EXTENSION=".svg"


def pipeRunning(tempDir):
    pipeName = os.path.join(tempDir,PTY_FILE)
    try:
        os.stat(pipeName)
        return True
    except:
        return False

def detectArduino(tempDir):
    global ARDUINO_DEV, ARDUINO_BOARD
    if ARDUINO_DEV == 'auto':
        try:
            print('looking for uno')
            os.stat('/dev/ttyACM0')
            print('found an uno!')
            ARDUINO_DEV='/dev/ttyACM0'
            ARDUINO_BOARD='uno'
        except:
            pass
    if ARDUINO_DEV == 'auto':
        try:
            print('looking for deum:')
            os.stat('/dev/ttyUSB0')
            print('found a deum')
            ARDUINO_DEV='/dev/ttyUSB0'
            ARDUINO_BOARD='atmega328'
        except:
            return None,None,None,None
    if USE_SERIAL_PIPE:
        print('devices: ',ARDUINO_DEV,os.path.join(tempDir,PTY_FILE),ARDUINO_BOARD,'software')
        return ARDUINO_DEV,os.path.join(tempDir,PTY_FILE),ARDUINO_BOARD,'software'
    else:
        print('devices: ',ARDUINO_DEV,ARDUINO_DEV,ARDUINO_BOARD,'hardware')
        return ARDUINO_DEV,ARDUINO_DEV,ARDUINO_BOARD,'hardware'

def startSerialPipe(hardwareDev,arduinoDev):
    call = SOCAT+' pty,raw,echo=0,link='+arduinoDev+',mode=666 '+ hardwareDev+',raw,echo=0,b1000000'
    print('call for socat is: ',call)
    args=shlex.split(call)
    try:
        subprocess.Popen(args)
        return True
    except:
        return False



def killSerialPipe(tempDir):
    head,tail = os.path.split(SOCAT)
    call = KILLALL + ' '+ tail
    args =shlex.split(call)
    print('trying to kill socat with: ',call)
    try:
        subprocess.Popen(args)
        time.sleep(.05) # need to let the kill do its thing before we check to see if it worked.
        print('call to kill socat completed')
    except:
        pass
    if pipeRunning(tempDir) == False:
        return True
    return False
