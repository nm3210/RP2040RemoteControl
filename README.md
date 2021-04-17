# RP2040 RemoteControl
Collection of microcontroller projects to 'remote control' another device, including miscellaneous testing scripts.

These scripts are to be used within the CircuitPython framework, mostly using the RP2040 chipset. I will not be including any of the required libraries within this repo, however, they'll be linked/referenced where necessary. Most of the scripts will be prepended with `main_` to facilitate renaming them to -> `main.py` on the device's storage (I haven't figured out a better workflow yet).

## Main Projects:
* [nRF24_RemoteControl](nRF24_RemoteControl): This contains the main scripts to setup boards to act as transmitter and receiver nodes of a basic remote control, sending commands from one to the other.

    This will potentially be used to control the modes of a string of lights by sending it different commands ("off", "on, white", etc.). The mechanism to select the mode may be via an accelerometer within a platonic solid (up = mode1, left side = mode3, etc).
    
    In preliminary testing, the nRF24L01 modules I have seemed to behave poorly when connected to an original ('OG') Raspberry Pi Pico RP2040 (using pins: sck=board.GP2, mosi=board.GP3, miso=board.GP4, csn=board.GP5, & ce=board.GP6). Specifically, I never got the OG Pico to successfully receive a message (transmitting via a Sparkfun Pro Micro RP2040).
    
    My best transmission result was when using two (x2) Sparkfun Pro Micro RP2040's with nRF24L01 'adapter boards' (using pins: spi=board.spi on D20,D22,D23, csn=board.D21, & ce = board.D5) where I got almost all messages successfully transmitted and received (with ack's back and everything).

## Testing & Prototyping Projects:
* [MPU6050_Testing](MPU6050_Testing): Handful of scripts to test the MPU6050 accelerometer sensor

* [nRF24_Testing](nRF24_Testing): Scripts to test the nRF24L01 transceiver, mostly copied over from https://github.com/2bndy5/CircuitPython_nRF24L01/tree/master/examples after adjusting for the pins I have set up.
