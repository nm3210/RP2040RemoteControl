# Testing MPU6050 Functionality
#
# nm3210@gmail.com
# Date Created: April 9th, 2021
# Last Modified: April 10th, 2021
#
# Sources for some of the code:
#   https://hridaybarot.home.blog/2021/03/23/controlling-asphalt-8-with-hand-gestures-using-mpu6050-and-raspberry-pi-pico/

# Import modules
import board, bitbangio, time # circuitpython built-ins
from math import floor, atan2, acos, sqrt, pi # necessary math calls
import adafruit_mpu6050 # also requires adafruit_register
import neopixel # also requires adafruit_pypixelbuf
print("Finished importing modules")

# Initialize soft I2C
softScl = board.D2 # manual serial clock line
softSdl = board.D3 # manual serial data line
i2c = bitbangio.I2C(softScl, softSdl) # software i2c
print("Finished initializing i2c")

# Initialize MPU6050 sensor
sensor = adafruit_mpu6050.MPU6050(i2c)
sensor.cycle_rate = adafruit_mpu6050.Rate.CYCLE_5_HZ # update cycle rate
sensor.cycle = True # only periodically update sensor (saves power!)
print("Finished initializing mpu6050")

# Setup calibrated accel values
numAvgValues = 25
listAccelX = [None] * numAvgValues
listAccelY = [None] * numAvgValues
listAccelZ = [None] * numAvgValues
listFaceIdx = [0] * numAvgValues

# Initialize neopixel output
ledPin = board.NEOPIXEL
colorOrder = neopixel.GRB # for the Sparkfun Pro Micro RP2040's WS2812
pixel = neopixel.NeoPixel(ledPin, 1, pixel_order=colorOrder)
print("Finished initializing neopixel")

# Setup colors and brightness settings
colorOff = (0,0,0)
colorRed = (255,0,0)
colorYellow = (255,255,0)
colorGreen = (0,255,0)
colorCyan = (0,255,255)
colorBlue = (0,0,255)
colorMagenta = (255,0,255)
brightness = 0.1 # from 0 to 1
    

### Private functions
def adjColor(_color, _brightness=1.0):
    return [floor(x * _brightness) for x in _color]
    
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


###
# Main LOOP
print("Starting main loop...")
while True:
    # Determine which face index is currently 'down'
    faceIdx = getSmoothedFaceIdx()
    
    # Change color!
    if faceIdx == 0: # invalid
        pixel[0] = adjColor(colorOff, brightness)
    elif faceIdx == 1: # invalid
        pixel[0] = adjColor(colorRed, brightness)
    elif faceIdx == 2: # invalid
        pixel[0] = adjColor(colorYellow, brightness)
    elif faceIdx == 3: # invalid
        pixel[0] = adjColor(colorGreen, brightness)
    elif faceIdx == 4: # invalid
        pixel[0] = adjColor(colorCyan, brightness)
    elif faceIdx == 5: # invalid
        pixel[0] = adjColor(colorBlue, brightness)
    elif faceIdx == 6: # invalid
        pixel[0] = adjColor(colorMagenta, brightness)

    time.sleep(0.01)