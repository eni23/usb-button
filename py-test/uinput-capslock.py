#!/usr/bin/env python

import time
import glob
import serial
import uinput
import subprocess

import ctypes
import ctypes.util


ENABLE_BIDIR_CAPS   = True
SERIAL_TIMEOUT      = 0.5
SERIAL_FIND_PAUSE   = 0.5
SERIAL_PORT_GLOB    = '/dev/ttyACM[0-9]'


def get_caps_lock_status():
    res = subprocess.check_output(
        'xset q | grep Caps | cut -d: -f3', shell=True
    ).decode().strip().split(" ")[0]
    if res == 'on':
        return True
    else:
        return False


def set_led_status(sdevice):
    if get_caps_lock_status():
        sdevice.write(b'1')
    else:
        sdevice.write(b'0')
    sdevice.read(1)


def find_and_open_serial():
    print("searching serial device")
    port_blacklist = []
    while True:
        ports = glob.glob(SERIAL_PORT_GLOB)
        for port in ports:
            if port in port_blacklist:
                continue
            print(f"trying {port}")
            try:
                ser = serial.Serial(
                    port = port,
                    timeout = SERIAL_TIMEOUT
                )
            except serial.serialutil.SerialException:
                print(f"port {port} blacklisted")
                port_blacklist.append(port)
                continue
            # check id string of device (ultra cheap)
            ser.write(b'9')
            res = ser.read(1)
            if res == b'r':
                print(f"found {port}")
                return ser
            else:
                print(f"id string not machtes for {port}")
                port_blacklist.append(port)

        print(".", end="", flush=True)
        time.sleep(SERIAL_FIND_PAUSE)


# simple variant
# def find_and_open_serial():
#     print("searching serial device")
#     serial_found = False
#     while not serial_found:
#         ports = glob.glob(SERIAL_PORT_GLOB)
#         if ports:
#             s = serial.Serial(
#                 port = ports[0],
#                 timeout = SERIAL_TIMEOUT
#             )
#             print("found")
#             return s
#         print(".", end="", flush=True)
#         time.sleep(SERIAL_FIND_PAUSE)


def device_emulator(sdevice, kdevice):
    while True:
        btn = sdevice.read(1)
        if btn == b'.':
            kdevice.emit_click(uinput.KEY_CAPSLOCK)
            set_led_status(sdevice)
        else:
            if ENABLE_BIDIR_CAPS:
                set_led_status(sdevice)


def main():
    kdevice = uinput.Device([
        uinput.KEY_CAPSLOCK
    ])
    while True:
        try:
            sdevice = find_and_open_serial()
            set_led_status(sdevice)
            device_emulator(sdevice, kdevice)
        except serial.serialutil.SerialException:
            time.sleep(1)
            continue


if __name__ == "__main__":
    main()
