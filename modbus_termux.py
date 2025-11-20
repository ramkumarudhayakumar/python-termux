# modbus_termux.py
import serial
import time

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
    def __init__(self, fd, timeout=1):
        self.fd_path = f"/proc/self/fd/{fd}"
        print("🔌 Opening serial using:", self.fd_path)

        self.ser = serial.Serial(
            self.fd_path,
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            timeout=timeout
        )

    def write(self, data: bytes):
        self.ser.write(data)

    def read(self, size: int):
        return self.ser.read(size)

    def read_register(self, slave, address):
        req = bytes([
            slave, 0x03,
            address >> 8, address & 0xFF,
            0x00, 0x01
        ])
        req += crc16(req)
        self.write(req)
        return self.read(8)

    def write_register(self, slave, address, value):
        req = bytes([
            slave, 0x06,
            address >> 8, address & 0xFF,
            value >> 8, value & 0xFF
        ])
        req += crc16(req)
        self.write(req)
        return self.read(8)
