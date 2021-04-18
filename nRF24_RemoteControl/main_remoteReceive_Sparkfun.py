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
# Last Modified: April 18th, 2021

# Import modules
import board, digitalio, struct, time, random # circuitpython built-ins
from math import floor # necessary math calls
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
colorOrder = neopixel.GRB # for the Sparkfun Pro Micro RP2040's WS2812
pixel = neopixel.NeoPixel(ledPin, 1, pixel_order=colorOrder)
pixel[0] = (0,0,0) # turn off on startup
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
    
def packPayload(data):
    return struct.pack("<f",data)
    
def unpackPayload(data):
    return struct.unpack("<f",data)

def receivePayload():
    nrf.listen = True # enable listen processing (high power usage)
    time.sleep(0.01) # allow listening on the radio for a while
    nrf.listen = False # disable listen processing (back to nominal power)
    
    if not nrf.available():
        return None
    
    # grab information about the received payload
    payload_size, pipe_number = (nrf.any(), nrf.pipe)
    
    # fetch 1 payload from RX FIFO
    buffer = nrf.read()  # also clears nrf.irq_dr status flag
    
    payload = unpackPayload(buffer)
    
    # print details about the received packet
    print(
        "Received {} bytes on pipe {}: {}".format(
            payload_size, pipe_number, payload[0]
        )
    )
    return payload[0]


###
# Main LOOP
print("Starting main loop for Remote Control - Receive...")
while True:
    # Send and check payload
    payloadContents = receivePayload()
    
    if payloadContents is not None:
        faceIdx = payloadContents
        # Change color!
        if faceIdx == 0: # invalid
            pixel[0] = adjColor(colorOff, brightness)
        elif faceIdx == 1:
            pixel[0] = adjColor(colorRed, brightness)
        elif faceIdx == 2:
            pixel[0] = adjColor(colorYellow, brightness)
        elif faceIdx == 3:
            pixel[0] = adjColor(colorGreen, brightness)
        elif faceIdx == 4:
            pixel[0] = adjColor(colorCyan, brightness)
        elif faceIdx == 5:
            pixel[0] = adjColor(colorBlue, brightness)
        elif faceIdx == 6:
            pixel[0] = adjColor(colorMagenta, brightness)
    