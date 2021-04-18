# Remote Control - Transmit
#   for use in the Sparkfun Pro Micro RP2040 board
#
# Default transmitter settings:
#   power level: -12 dB
#   transmit address: b"1Node"
#   receive address:  b"2Node"
# 
# nm3210@gmail.com
# Date Created:  April 17th, 2021
# Last Modified: April 17th, 2021

# Import modules
import board, digitalio, struct, time, random # circuitpython built-ins
import neopixel # also requires adafruit_pypixelbuf
from circuitpython_nrf24l01.rf24 import RF24
print("Finished importing modules")

# Initialize neopixel output
ledPin = board.NEOPIXEL
colorOrder = neopixel.GRB # for the Sparkfun Pro Micro RP2040's WS2812
pixel = neopixel.NeoPixel(ledPin, 1, pixel_order=colorOrder)
pixel[0] = (0,0,0) # turn off on startup
print("Finished initializing neopixel")


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
txAddress = b"1Node" # transmit module tx pipe = '1Node'
rxAddress = b"2Node" # transmit module rx pipe = '2Node'
nrf.open_tx_pipe(txAddress)
nrf.open_rx_pipe(1, rxAddress)

# Set default state to 'off'
nrf.listen = False
nrf.power = False
print("Finished initializing nRF24 module")


### Private functions
def anyChanges():
    return True

def getPayload():
    dataToSend = random.random()
    return dataToSend

def packPayload(data):
    return struct.pack("<f",data)
    
def unpackPayload(data):
    return struct.unpack("<f",data)

def sendPayload():
    # Get the current payload
    payload = getPayload()
    
    # Configure the module to transmit
    nrf.power = True
    time.sleep(0.025)
    nrf.listen = False
    time.sleep(0.025)
    
    # Attempt to send the payload
    print(f'Attempting to send payload \'{payload}\'')
    numRetries = 4;
    gotAckBack = nrf.send(packPayload(payload), force_retry=numRetries)
    
    # Check whether the send was 'successful' (got an ack back)
    if gotAckBack == True:
        print(f'Succesfully sent payload \'{payload}\' (received ack back)')
    else:
        print(f'No ack was received back for payload \'{payload}\'')
    
    # Disable the module to hopefully conserve power
    nrf.power = False
    
    # Return value of whether an ack was received back
    return gotAckBack


###
# Main LOOP
print("Starting main loop...")
while True:
    # Check for changes to enable transmission
    if not anyChanges():
        continue
    
    # Send payload
    sendPayload()

    # Wait
    time.sleep(1.0)

