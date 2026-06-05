# Iambic Morse keyer — Raspberry Pi Pico (CircuitPython + USB HID)
# Wiring:
#   DIT paddle tip  → GP6 (Pin 9)
#   DAH paddle ring → GP4 (Pin 6)
#   Sleeve / common → GND (Pin 8)
#   Sidetone speaker→ GP5 (Pin 7)
#
# Requires CircuitPython firmware + adafruit_hid library in /lib

import board, time, pwmio, digitalio, usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# ── pin setup ──────────────────────────────────────────────
dit_pin = digitalio.DigitalInOut(board.GP6)
dit_pin.direction = digitalio.Direction.INPUT
dit_pin.pull = digitalio.Pull.UP                  # active LOW

dah_pin = digitalio.DigitalInOut(board.GP4)
dah_pin.direction = digitalio.Direction.INPUT
dah_pin.pull = digitalio.Pull.UP                  # active LOW

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

sidetone = pwmio.PWMOut(board.GP5, frequency=700, duty_cycle=0, variable_frequency=False)

# ── HID keyboard ───────────────────────────────────────────
kbd    = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

# ── keyer config ───────────────────────────────────────────
WPM         = 15
DOT_S       = 1.2 / WPM                           # PARIS standard, in seconds
DEBOUNCE_S  = 0.010                               # 10 ms — increase if doubling
IAMBIC_B    = True                                # Curtis B mode

# ── Morse decode table ─────────────────────────────────────
MORSE = {
    ".-":"A",   "-...":"B", "-.-.":"C", "-..":"D",  ".":"E",
    "..-.":"F", "--.":"G",  "....":"H", "..":"I",   ".---":"J",
    "-.-":"K",  ".-..":"L", "--":"M",   "-.":"N",   "---":"O",
    ".--.":"P", "--.-":"Q", ".-.":"R",  "...":"S",  "-":"T",
    "..-":"U",  "...-":"V", ".--":"W",  "-..-":"X", "-.--":"Y",
    "--..":"Z",
    ".----":"1","..---":"2","...--":"3","....-":"4",".....":"5",
    "-....":"6","--...":"7","---..":"8","----.":"9","-----":"0",
    ".-.-.-":".", "--..--":",", "..--..":"?", ".----.":"'",
    "-.-.--":"!", "-..-.": "/", "-.--.":"(", "-.--.-":")",
    ".-...":"&", "---...":":", "-.-.-.":";", "-...-":"=",
    ".-.-.":"+", "-....-":"-", "..--.-":"_", ".-..-.":'"',
    "...-..-":"$", ".--.-.":"@"
}

# ── helpers ────────────────────────────────────────────────
def beep(duration):
    sidetone.duty_cycle = 32768
    led.value = True
    time.sleep(duration)
    sidetone.duty_cycle = 0
    led.value = False
    time.sleep(DEBOUNCE_S)               # debounce gap after element

def send_dit():
    beep(DOT_S)
    time.sleep(DOT_S)                    # inter-element gap

def send_dah():
    beep(DOT_S * 3)
    time.sleep(DOT_S)                    # inter-element gap

def type_char(buf):
    if not buf:
        return
    ch = MORSE.get(buf)
    if ch:
        layout.write(ch)                 # → USB HID keyboard to host
    else:
        layout.write("?")

# ── main keyer loop ────────────────────────────────────────
def run_keyer():
    buf     = ""
    last_el = time.monotonic()
    mem_dit = False
    mem_dah = False

    while True:
        dit = not dit_pin.value
        dah = not dah_pin.value

        if dit or mem_dit:
            send_dit()
            buf    += "."
            mem_dit = False
            if IAMBIC_B:
                mem_dah = not dah_pin.value
            last_el = time.monotonic()

        elif dah or mem_dah:
            send_dah()
            buf    += "-"
            mem_dah = False
            if IAMBIC_B:
                mem_dit = not dit_pin.value
            last_el = time.monotonic()

        else:
            elapsed = time.monotonic() - last_el

            # letter gap → decode and type the character
            if buf and elapsed > DOT_S * 2.5:
                type_char(buf)
                buf     = ""
                last_el = time.monotonic()

            # word gap → type a space (only once per idle period)
            elif not buf and elapsed > DOT_S * 6:
                layout.write(" ")
                last_el = float('inf')   # park so it never fires again until next keypress

        time.sleep(0.001)                # small yield

run_keyer()
