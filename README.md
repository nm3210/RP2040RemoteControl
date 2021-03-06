# RP2040 RemoteControl

Collection of microcontroller projects to 'remote control' another device, including miscellaneous testing scripts.

These scripts are to be used within the CircuitPython framework, mostly using the RP2040 chipset. I will not be including any of the required libraries within this repo, however, they'll be linked/referenced where necessary. Most of the scripts will be prepended with `main_` to facilitate renaming them to -> `main.py` on the device's storage (I haven't figured out a better workflow yet).

## Main Projects

* [nRF24_RemoteControl](nRF24_RemoteControl): This contains the main scripts to setup boards to act as transmitter and receiver nodes of a basic remote control, sending commands from one to the other.

    This will potentially be used to control the modes of a string of lights by sending it different commands ("off", "on, white", etc.). The mechanism to select the mode may be via an accelerometer within a platonic solid (up = mode1, left side = mode3, etc).

    The receive module has been setup with an OshPark pcb to accept a Sparkfun Pro Micro with an rRF24L01 module on top of it.

    [![front](https://644db4de3505c40a0444-327723bce298e3ff5813fb42baeefbaa.ssl.cf1.rackcdn.com/7278f274c43d13a2ca392a091e58a9ee.png) ![back](https://644db4de3505c40a0444-327723bce298e3ff5813fb42baeefbaa.ssl.cf1.rackcdn.com/6ac03391f8f8bb451b62ce8364d421eb.png)](https://oshpark.com/shared_projects/c06FLb7A)

    The transmit module, however, is planned to be a [Sparkfun Thing Plus RP2040](https://www.sparkfun.com/products/17745) so that a battery can be used (the Thing Plus features a battery input and a handful of battery related circuits onboard).

## Testing & Prototyping Projects

* [MPU6050_Testing](MPU6050_Testing): Handful of scripts to test the MPU6050 accelerometer sensor

* [nRF24_Testing](nRF24_Testing): Scripts to test the nRF24L01 transceiver, mostly copied over from <https://github.com/2bndy5/CircuitPython_nRF24L01/tree/master/examples> after adjusting for the pins I have set up.

* [ColorDescriptors](https://github.com/nm3210/ColorDescriptors): Easily defined color descriptor words to be passed from one node to another

* [EasyStreamNrf24](https://github.com/nm3210/EasyStreamNrf24): Extends the normal NRF send/receive commands to combine multiple consecutive packets together