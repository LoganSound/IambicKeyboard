https://youtube.com/shorts/-fLk9oqEUls?si=KVMjBsyJLu_AhUqc
AI Disclosure: this was made with Claude

Bill of Materials
-Raspberry Pi Pico and USB cable
-Iambic paddle with TRS output
-TRS audio cable (or half of one at least)
-soldering iron, solder though probably possible with a breadboard

Hardware Design

Pinout diagram — visual Pico chip with color-coded pins (GP6=DIT, GP4=DAH, GP5=sidetone)
Circuit schematic — shows the full signal path: paddle → 10 kΩ protection resistors → Pico GPIO → USB to host, with sidetone low-pass filter and speaker
Bill of Materials — everything you need (Pico, TRS jack, two resistors, cap, piezo speaker)

Wiring summary
Paddle contactPico pinNoteDIT tipGP2 Active LOW, internal pull-upDAH ringGP4 Active LOW, internal pull-upSleeveGND (Pin 3)CommonSidetoneGP5 (Pin 7)PWM audio
Firmware — MicroPython main.py implementing Curtis B iambic mode with paddle memory, sidetone beep, and decoded text output over USB

Step 1 — Flash HID-enabled MicroPython
Download the community build that includes USB HID:

Go to https://github.com/Neradoc/circuitpython-keyboard-layouts — actually, simpler:
Use Adafruit CircuitPython instead of MicroPython; HID is built in and well supported

Flash it:

Hold BOOTSEL on the Pico while plugging in USB — it mounts as a drive called RPI-RP2
Drag and drop the .uf2 file onto that drive
It reboots automatically as a CircuitPython device

Download the CircuitPython UF2 for Pico here: https://circuitpython.org/board/raspberry_pi_pico
Step 2 — Install the HID library
Download the CircuitPython library bundle from https://circuitpython.org/libraries, then copy adafruit_hid from the bundle into the lib/ folder on the Pico's USB drive.
Step 3 — Replace main.py
