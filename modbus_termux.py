# modbus_termux.py
import subprocess
import os
import serial

def crc16(data: bytes):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, "little")


class TermuxUSBModbus:
    def __init__(self):
        # Get USB device list
        result = subprocess.check_output(["termux-usb", "-l"]).decode()
        if "/dev/bus/usb" not in result:
            raise Exception("No USB device found")

        dev = result.strip()[2:-2]     # extract path: "/dev/bus/usb/001/002"

        print("📦 USB Device:", dev)

        # Request read/write access
        p = subprocess.Popen(["termux-usb", "-r", dev], stdin=subprocess.PIPE)
        print("⚡ Waiting for USB FD...")

        # Read FD number from stdin
        fd = int(p.stdin.fileno())

        print("🔌 Using FD:", fd)

        self.fd_path = f"/proc/self/fd/{fd}"

        self.ser = serial.Serial(
            self.fd_path,
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            timeout=1
        )

    def write(self, data: bytes):
        self.ser.write(data)

    def read(self, n: int):
        return self.ser.read(n)

    def read_register(self, slave, addr):
        req = bytes([slave, 0x03, addr >> 8, addr & 0xFF, 0x00, 0x01])
        req += crc16(req)
        self.write(req)
        return self.read(8)

    def write_register(self, slave, addr, val):
        req = bytes([slave, 0x06, addr >> 8, addr & 0xFF, val >> 8, val & 0xFF])
        req += crc16(req)
        self.write(req)
        return self.read(8)
