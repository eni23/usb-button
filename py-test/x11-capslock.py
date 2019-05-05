#!/usr/bin/env python

import sys
import time
import glob
import serial
import subprocess

import ctypes
import ctypes.util


ENABLE_BIDIR_CAPS   = True
SERIAL_TIMEOUT      = 0.2
SERIAL_FIND_PAUSE   = 0.5
SERIAL_PORT_GLOB    = '/dev/ttyACM[0-9]'


class x11Capslock:
    class Display(ctypes.Structure):
        _fields_ = []

    def __init__(self):
        self.x11 = ctypes.cdll.LoadLibrary(
            ctypes.util.find_library('X11')
        )
        self.x11.XOpenDisplay.restype = ctypes.POINTER(self.Display)
        self.display = self.x11.XOpenDisplay(ctypes.c_int(0))
        self.res = (ctypes.c_uint*1)()

    def get(self):
        self.x11.XkbGetIndicatorState(
            self.display,
            ctypes.c_uint(0x0100),
            self.res
        )
        if self.res[0]==1:
            return True
        return False

    def set(self, state):
        state = 2 if state is True else 0
        self.x11.XkbLockModifiers(
            self.display,
            ctypes.c_uint(0x0100),
            ctypes.c_uint(18),
            ctypes.c_uint(state),
        )
        self.flush()

    def flush(self):
        self.x11.XFlush(self.display)

    def close(self):
        self.x11.XCloseDisplay(self.display)




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






def set_led_status(sdevice, capslock):
    sdevice.write(
        b'1' if capslock.get() is True else b'0'
    )
    sdevice.read(1)


def device_emulator(sdevice, capslock):
    while True:
        btn = sdevice.read(1)
        if btn == b'.':
            capslock.set(
                True if capslock.get() is False else False
            )
            set_led_status(sdevice, capslock)
        else:
            if ENABLE_BIDIR_CAPS:
                set_led_status(sdevice, capslock)


def main():
    capslock = x11Capslock()
    while True:
        try:
            sdevice = find_and_open_serial()
            set_led_status(sdevice, capslock)
            try:
                device_emulator(sdevice, capslock)
            except KeyboardInterrupt:
                capslock.close()
                sdevice.flush()
                sdevice.close()
                sys.exit(0)
        except serial.serialutil.SerialException:
            time.sleep(1)
            continue


if __name__ == "__main__":
    main()
