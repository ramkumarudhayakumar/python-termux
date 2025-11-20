import os
import serial

class TermuxUSBModbus:
    def __init__(self, fd):
        self.fd = fd
        self.dev_path = f"/proc/self/fd/{fd}"

        self.ser = serial.Serial(
            port=self.dev_path,
            baudrate=19200,
            bytesize=8,
            stopbits=2,
            parity=serial.PARITY_NONE,
            timeout=5
        )

    def write(self, data):
        print("👉 Writing:", data.hex())
        self.ser.write(data)

    def read(self, size=8):
        response = self.ser.read(size)
        print("👈 Read:", response.hex())
        return response

    def close(self):
        self.ser.close()
