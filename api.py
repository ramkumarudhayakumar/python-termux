from flask import Flask, jsonify
from modbus_termux import TermuxUSBModbus
import sys
import time

app = Flask(__name__)

SLAVE = 1
HOLDING = 0    # 40001
STATUS = 0     # 30001

# Get USB FD from termux-usb
device_fd = f"/proc/self/fd/{sys.argv[1]}"
modbus = TermuxUSBModbus(device_fd)


@app.route("/check/modbus/connection")
def check_conn():
    resp = modbus.read_register(SLAVE, HOLDING)
    if len(resp) < 8:
        return jsonify({"success": False, "message": "No response"}), 400

    value = int.from_bytes(resp[3:5], "big")

    return jsonify({
        "success": True,
        "message": "Modbus connected",
        "value": value
    })


@app.route("/modbus/status")
def status():
    resp = modbus.read_register(SLAVE, STATUS)
    if len(resp) < 8:
        return jsonify({"success": False}), 400

    value = int.from_bytes(resp[3:5], "big")
    return jsonify({"success": True, "status": value})


@app.route("/start/motor/<int:motor_id>", methods=["POST"])
def start_motor(motor_id):

    # 1. Write command
    wr = modbus.write_register(SLAVE, HOLDING, motor_id)
    if len(wr) < 8:
        return jsonify({"success": False, "message": "Write failed"}), 400

    # 2. Read status loop
    timeout = time.time() + 10
    while time.time() < timeout:
        resp = modbus.read_register(SLAVE, STATUS)
        if len(resp) < 8:
            continue

        status = int.from_bytes(resp[3:5], "big")

        if status in [1, 2, 3]:
            msg = {1: "Started", 2: "Processing", 3: "Completed"}[status]
            return jsonify({"success": True, "status": status, "message": msg})

        if status in [26, 27, 28]:
            err = {
                26: "Emergency Stop",
                27: "Elevator down limit",
                28: "Elevator left limit"
            }[status]
            return jsonify({"success": False, "status": status, "message": err})

        time.sleep(0.2)

    return jsonify({"success": False, "message": "Timeout"}), 408


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
