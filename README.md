# RP2040 RemoteControl
Collection of microcontroller projects to 'remote control' another device, including miscellaneous testing scripts.

These scripts are to be used within the CircuitPython framework, mostly using the RP2040 chipset. I will not be including any of the required libraries within this repo, however, they'll be linked/referenced where necessary. Most of the scripts will be prepended with `main_` to facilitate renaming them to -> `main.py` on the device's storage (I haven't figured out a better workflow yet).

## Testing & Prototyping Projects:
* [MPU6050_Testing](MPU6050_Testing): Handful of scripts to test the MPU6050 accelerometer sensor

* [nRF24_Testing](nRF24_Testing): Scripts to test the nRF24L01 transceiver, mostly copied over from https://github.com/2bndy5/CircuitPython_nRF24L01/tree/master/examples after adjusting for the pins I have set up.
