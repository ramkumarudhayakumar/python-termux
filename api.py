from flask import Flask, jsonify
from modbus_termux import TermuxUSBModbus
import time

app = Flask(__name__)

SLAVE = 1
HOLD = 0
STATUS = 0

print("🔍 Initializing USB Modbus...")
modbus = TermuxUSBModbus()
print("✅ Modbus Ready")


@app.route("/check")
def check():
    resp = modbus.read_register(SLAVE, HOLD)
    if len(resp) < 7:
        return {"success": False, "msg": "No response"}, 400

    value = int.from_bytes(resp[3:5], "big")
    return {"success": True, "value": value}


@app.route("/start/<int:motor>", methods=["POST"])
def start(motor):
    wr = modbus.write_register(SLAVE, HOLD, motor)

    if len(wr) < 8:
        return {"success": False, "msg": "Write failed"}, 400

    timeout = time.time() + 10
    while time.time() < timeout:
        resp = modbus.read_register(SLAVE, STATUS)
        if len(resp) < 7:
            continue

        st = int.from_bytes(resp[3:5], "big")

        if st in [1, 2, 3]:
            return {"success": True, "status": st}

        if st in [26, 27, 28]:
            return {"success": False, "status": st}

    return {"success": False, "msg": "Timeout"}, 408


app.run(host="0.0.0.0", port=5000)
