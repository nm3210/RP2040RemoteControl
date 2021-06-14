# Remote Control - Receive
#   for use in the Sparkfun Pro Micro RP2040 board
#
# Default receiver settings:
#   power level: -12 dB
#   transmit address: b"2Node"
#   receive address:  b"1Node"
# 
# nm3210@gmail.com
# Date Created:  April 17th, 2021
# Last Modified: June 13th, 2021

# Import modules
import board, digitalio, struct, time, random # circuitpython built-ins
from math import floor # necessary math calls
import neopixel # also requires adafruit_pypixelbuf
from circuitpython_nrf24l01.rf24 import RF24
from lib.ColorDescriptors.ColorDescriptors import *
from lib.EasyStreamNrf24.EasyStreamNrf24 import receivePayload
print("Finished importing modules")

### Initialize nRF24L01
# Configure pinouts
ce = digitalio.DigitalInOut(board.D26)
csn = digitalio.DigitalInOut(board.D21)
spi = board.SPI() # init spi bus w/ pins D[20,22,23]
irq = digitalio.DigitalInOut(board.D27) # optional IRQ pin to listen to interupts

# Initialize object
nrf = RF24(spi, csn, ce)

# Configure settings
irq.switch_to_input()  # make sure its an input object
nrf.pa_level = -12 # low for close-proximity testing

# Select tx/rx addresses
txAddress = b"2Node" # receive module tx pipe = '2Node'
rxAddress = b"1Node" # receive module rx pipe = '1Node'
nrf.open_tx_pipe(txAddress)
nrf.open_rx_pipe(1, rxAddress)

# Set state to conserve power until needed
nrf.listen = False
print("Finished initializing nRF24 module")


### Initialize neopixel output
ledPin = board.NEOPIXEL
pixelMain = neopixel.NeoPixel(ledPin, 1, pixel_order=neopixel.GRB)
pixelMain[0] = (0,0,0) # turn off on startup

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


### Other things
# Setup some storage vars
faceColor = ColorSolid(intensity=0)

# Configure timers
timeCheck_receive = time.monotonic_ns()
updateTime_receive = 0.01 # seconds, how often to listen
updateDur_receive = 0.011 # seconds, how long to listen

### Private functions
def adjColor(_color, _brightness=1.0):
    return [floor(x * _brightness) for x in _color]


###
# Main LOOP
print("Starting main loop for Remote Control - Receive...")
while True:
    ### Check timers
    # Listen to the RF interface for any incoming messages
    detectedChanges = False
    if abs(time.monotonic_ns() - timeCheck_receive) > updateTime_receive*1e9:
        timeCheck_receive = time.monotonic_ns() # reset timer
        
        # Check if the payload is valid (not none)
        payloadContents = receivePayload(nrf, debugPrint=False)
        if payloadContents is not None:
            try: # don't crash if the payload can't be converted correctly
                # Convert to a color
                curColor = ColorSolid.parse(payloadContents)
                if faceColor != curColor:
                    detectedChanges = True
                
                # Store the payload as the last valid content received
                faceColor = curColor
            except:
                try:
                    faceIdx = float(payloadContents)
                    curColor = ColorSolid(hue=((faceIdx-1)*60.0))
                    if faceColor != curColor:
                        detectedChanges = True
                    
                    # Store the payload as the last valid content received
                    faceColor = curColor
                except:
                    pass

    ### Update
    if detectedChanges == True:
        # Change color!
        pixelMain.fill(adjColor((faceColor.red, faceColor.green, faceColor.blue),brightness))
    
    