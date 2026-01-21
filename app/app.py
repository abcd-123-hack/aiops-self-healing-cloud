import logging
from flask import Flask, jsonify
import threading
import time

logging.basicConfig(
    filename="/home/ec2-user/aiops-app/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Flask(__name__)

cpu_stress_running = False

@app.route("/")
def home():
    return "AIOps Self-Healing App is running", 200

import logging

logging.basicConfig(level=logging.INFO)

@app.route("/health")
def health():
    if cpu_stress_running:
        logging.error("APP_HEALTH_FAIL")
        return jsonify({"status": "degraded"}), 500
    return jsonify({"status": "ok"}), 200


def cpu_stress():
    global cpu_stress_running
    cpu_stress_running = True
    end_time = time.time() + 120  # stress for 2 minutes
    while time.time() < end_time:
        pass
    cpu_stress_running = False


@app.route("/stress")
def stress():
    global cpu_stress_running

    if not cpu_stress_running:
        thread = threading.Thread(target=cpu_stress)
        thread.start()

    return "CPU stress started"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
