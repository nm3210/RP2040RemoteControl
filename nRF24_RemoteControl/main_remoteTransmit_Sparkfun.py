# Remote Control - Transmit
#   for use in the Sparkfun Pro Micro RP2040 board
#
# Default transmitter settings:
#   power level: 0 dB (maximum)
#   transmit address: b"1Node"
#   receive address:  b"2Node"
# 
# nm3210@gmail.com
# Date Created:  April 17th, 2021
# Last Modified: June 13th, 2021

# Import modules
import board, bitbangio, digitalio, struct, time, random # circuitpython built-ins
from math import atan2, acos, sqrt, pi # necessary math calls
import adafruit_mpu6050 # also requires adafruit_register
import neopixel # also requires adafruit_pypixelbuf
from circuitpython_nrf24l01.rf24 import RF24
from lib.ColorDescriptors.ColorDescriptors import *
from lib.EasyStreamNrf24.EasyStreamNrf24 import sendPayload
print("Finished importing modules")

### Initialize nRF24L01
# Configure pinouts
ce = digitalio.DigitalInOut(board.D5)
csn = digitalio.DigitalInOut(board.D21)
spi = board.SPI() # init spi bus w/ pins D[20,22,23]
irq = digitalio.DigitalInOut(board.D6) # optional IRQ pin to listen to interupts

# Initialize object
nrf = RF24(spi, csn, ce)

# Configure settings
irq.switch_to_input()  # make sure its an input object
nrf.pa_level = 0 # maximum

# Select tx/rx addresses
txAddress = b"1Node" # transmit module tx pipe = '1Node'
rxAddress = b"2Node" # transmit module rx pipe = '2Node'
nrf.open_tx_pipe(txAddress)
nrf.open_rx_pipe(1, rxAddress)

# Set default state to 'off'
nrf.listen = False
nrf.power = False
print("Finished initializing nRF24 module")


### Initialize neopixel output
ledPin = board.NEOPIXEL
pixelMain = neopixel.NeoPixel(ledPin, 1, pixel_order=neopixel.GRB)
pixelMain.fill((0,0,0)) # turn off on startup
print("Finished initializing neopixel")


### Initialize MPU6050 sensor
# Initialize soft I2C
softScl = board.D2 # manual serial clock line
softSdl = board.D3 # manual serial data line
i2c = bitbangio.I2C(softScl, softSdl) # software i2c

# Initialize MPU6050 object
sensor = adafruit_mpu6050.MPU6050(i2c)
sensor.cycle_rate = adafruit_mpu6050.Rate.CYCLE_40_HZ # update cycle rate
sensor.cycle = True # only periodically update sensor (saves power!)
print("Finished initializing mpu6050")

# Setup calibrated accel values
numAvgValues = 5
listAccelX = [None] * numAvgValues
listAccelY = [None] * numAvgValues
listAccelZ = [None] * numAvgValues
listFaceIdx = [0] * numAvgValues


### Other things
# Setup some storage vars
lastFace = 0

# Configure timers
timeCheck_faceIdx = time.monotonic_ns()
updateTime_faceIdx = 1.1/40 # seconds, enough time for the 40 Hz to update

timeCheck_changes = time.monotonic_ns()
updateTime_changes = 0.01 # seconds

timeCheck_autosend = time.monotonic_ns()
updateTime_autosend = 1.0 # always send an update every once in a while


### Private functions
def getDownwardFaceIndex():
    # Collect sensor updates
    theta, phi = getAccelTiltAngle() # in degrees
    
    # Determine sides of the platonic cube
    angleCheck = 20
    return getPlatonicCubeFaceIdx(theta, phi, angleCheck)

def getPlatonicCubeFaceIdx(theta, phi, angleCheck):
    # Determine sides of the platonic cube
    faceIdx = 0 # invalid face
    angleDiff = lambda start, stop : ((start-stop)+180)%360 - 180
    if   abs(angleDiff(theta,  0)) <= angleCheck and abs(angleDiff(phi, 90)) <= angleCheck: # Down
        faceIdx = 1
    elif abs(angleDiff(theta,180)) <= angleCheck and abs(angleDiff(phi, 90)) <= angleCheck: # Up
        faceIdx = 2
    elif abs(angleDiff(theta,-90)) <= angleCheck and abs(angleDiff(phi, 90)) <= angleCheck: # Side 1
        faceIdx = 3
    elif abs(angleDiff(theta, 90)) <= angleCheck and abs(angleDiff(phi, 90)) <= angleCheck: # Side 2
        faceIdx = 4
    elif abs(angleDiff(phi,  0)) <= angleCheck: # Side 3, no theta check necessary because it's in a singularity
        faceIdx = 5
    elif abs(angleDiff(phi,180)) <= angleCheck: # Side 4, no theta check necessary because it's in a singularity
        faceIdx = 6
    else:
        pass
    return faceIdx

def getAccelTiltAngle():
    # via https://www.analog.com/en/app-notes/an-1057.html eq 9 & 10
    x, y, z = getSmoothedAccel()
    theta = atan2(y, x) # (-180,180)
    phi = acos(z / sqrt(x*x + y*y + z*z)) # (0,180)
    return theta*180/pi, phi*180/pi # -> deg

def getSmoothedAccel():
    preallocateAccelList() # first time only, via simply none check
    
    # Update the sensor
    updateAccelList()
    
    # Calculate the 'moving' average
    x = sum(listAccelX) / len(listAccelX)
    y = sum(listAccelY) / len(listAccelY)
    z = sum(listAccelZ) / len(listAccelZ)
    return x, y, z

def updateAccelList():
    """
    Updates the acceleration lists with a new sensor value
    """
    # Get new sensor update/s
    x, y, z = getSensorAccel()
    
    # Pop out old values (idx 0)
    listAccelX.pop(0) # ignore outgoing value
    listAccelY.pop(0) # ignore outgoing value
    listAccelZ.pop(0) # ignore outgoing value
    
    # Append the new values
    listAccelX.append(x)
    listAccelY.append(y)
    listAccelZ.append(z)

def getSmoothedFaceIdx():
    if not all(ele == listFaceIdx[0] for ele in listFaceIdx):
        return 0 # ALL elements need to be identical to return a valid value
    return listFaceIdx[0]

def updateFaceIdx():
    _faceIdx = getDownwardFaceIndex()
    listFaceIdx.pop(0) # remove an entry (ignore outgoing value)
    listFaceIdx.append(_faceIdx) # add the new index

def preallocateAccelList():
    # Check if there are any none's to replace
    while (None in listAccelX or None in listAccelY or None in listAccelY):
        updateAccelList()
        time.sleep(1.1/40) # wait for the sensor to update

def getSensorAccel():
    x, y, z = sensor.acceleration
    return x, y, z

def anyChanges():
    global lastFace
    currentFace = getSmoothedFaceIdx()
    if currentFace != 0 and currentFace != lastFace:
        lastFace = currentFace
        return True
    return False

def getPayload():
    global lastFace
    return str(lastFace)

###
# Main LOOP
print("Starting main loop for Remote Control - Transmit...")
while True:
    ### Check timers
    # Update FaceIdx
    if abs(time.monotonic_ns() - timeCheck_faceIdx) > updateTime_faceIdx*1e9:
        timeCheck_faceIdx = time.monotonic_ns() # reset timer
        updateFaceIdx()
    
    # Check for any face index changes
    detectedChanges = False
    if abs(time.monotonic_ns() - timeCheck_changes) > updateTime_changes*1e9:
        timeCheck_changes = time.monotonic_ns() # reset timer
        detectedChanges = anyChanges()
    
    # Send an update if any changes or a timeout has been reached
    if lastFace != 0 and (detectedChanges or abs(time.monotonic_ns() - timeCheck_autosend) > updateTime_autosend*1e9):
        timeCheck_autosend = time.monotonic_ns() # reset timer
        sendPayload(nrf, getPayload(), debugPrint=False)
    