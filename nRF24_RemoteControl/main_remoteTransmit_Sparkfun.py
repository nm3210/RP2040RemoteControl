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
# Last Modified: April 18th, 2021

# Import modules
import board, bitbangio, digitalio, struct, time, random # circuitpython built-ins
from math import atan2, acos, sqrt, pi # necessary math calls
import adafruit_mpu6050 # also requires adafruit_register
import neopixel # also requires adafruit_pypixelbuf
from circuitpython_nrf24l01.rf24 import RF24
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
colorOrder = neopixel.GRB # for the Sparkfun Pro Micro RP2040's WS2812
pixel = neopixel.NeoPixel(ledPin, 1, pixel_order=colorOrder)
pixel[0] = (0,0,0) # turn off on startup
print("Finished initializing neopixel")


### Initialize MPU6050 sensor
# Initialize soft I2C
softScl = board.D2 # manual serial clock line
softSdl = board.D3 # manual serial data line
i2c = bitbangio.I2C(softScl, softSdl) # software i2c

# Initialize MPU6050 object
sensor = adafruit_mpu6050.MPU6050(i2c)
sensor.cycle_rate = adafruit_mpu6050.Rate.CYCLE_5_HZ # update cycle rate
sensor.cycle = True # only periodically update sensor (saves power!)
print("Finished initializing mpu6050")

# Setup calibrated accel values
numAvgValues = 15
listAccelX = [None] * numAvgValues
listAccelY = [None] * numAvgValues
listAccelZ = [None] * numAvgValues
listFaceIdx = [0] * numAvgValues


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
    updateFaceIdx()
    if not all(ele == listFaceIdx[0] for ele in listFaceIdx):
        return 0 # ALL elements need to be identical to return a valid face
    return listFaceIdx[0]

def updateFaceIdx():
    _faceIdx = getDownwardFaceIndex()
    listFaceIdx.pop(0) # ignore outgoing value
    listFaceIdx.append(_faceIdx)

def preallocateAccelList():
    # Check if there are any none's to replace
    while (None in listAccelX or None in listAccelY or None in listAccelY):
        updateAccelList()
        time.sleep(0.05) # wait a bit

def getSensorAccel():
    x, y, z = sensor.acceleration
    return x, y, z

def anyChanges():
    return True

def getPayload():
    return getSmoothedFaceIdx()

def packPayload(data):
    return struct.pack("<f",data)
    
def unpackPayload(data):
    return struct.unpack("<f",data)

def sendPayload():
    # Get the current payload
    payload = getPayload()
    
    # Configure the module to transmit
    nrf.power = True
    nrf.listen = False
    
    # Attempt to send the payload
    print(f'Attempting to transmit payload \'{payload}\'')
    numRetries = 4;
    gotAckBack = nrf.send(packPayload(payload), force_retry=numRetries)
    
    # Check whether the send was 'successful' (got an ack back)
    if gotAckBack == True:
        print(f'  Succesfully transmitted payload \'{payload}\' (received ack back)')
    else:
        print(f'  No ack was received back for payload \'{payload}\'')
    
    # Disable the module to hopefully conserve power
    nrf.power = False
    
    # Return value of whether an ack was received back
    return gotAckBack


###
# Main LOOP
print("Starting main loop for Remote Control - Transmit...")
while True:
    # Check for changes to enable transmission
    if not anyChanges():
        continue
    
    # Send payload
    sendPayload()

    # Wait
    time.sleep(0.25)

