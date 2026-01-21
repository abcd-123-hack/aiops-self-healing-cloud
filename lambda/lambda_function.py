import boto3
import time
from decimal import Decimal

cloudwatch = boto3.client("cloudwatch")
dynamodb = boto3.resource("dynamodb")
ssm = boto3.client("ssm")

TABLE_NAME = "aiops_incidents"
COOLDOWN_SECONDS = 600  # 10 minutes
INSTANCE_ID = "i-XXXXXXXXXXXX"  # <-- replace with your EC2 ID


# ---------- Helpers ----------

def get_alarm_states():
    response = cloudwatch.describe_alarms(StateValue="ALARM")
    states = {}
    for alarm in response.get("MetricAlarms", []):
        states[alarm["AlarmName"]] = alarm["StateValue"]
    return states


def record_incident(incident_id):
    table = dynamodb.Table(TABLE_NAME)
    now = int(time.time())

    response = table.get_item(Key={"incident_id": incident_id})

    if "Item" in response:
        last_seen = int(response["Item"]["last_seen"])
        count = int(response["Item"]["count"]) + 1
        cooldown_active = (now - last_seen) < COOLDOWN_SECONDS
    else:
        count = 1
        cooldown_active = False

    table.put_item(
        Item={
            "incident_id": incident_id,
            "last_seen": now,
            "count": count
        }
    )

    return count, cooldown_active


# ---------- Remediation Actions ----------

def restart_app():
    ssm.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": [
                "sudo pkill -f app.py",
                "python3 /home/ec2-user/aiops-app/app.py &"
            ]
        }
    )


def reboot_instance():
    ssm.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": ["sudo reboot"]
        }
    )


# ---------- Main Brain ----------

def lambda_handler(event, context):
    print("Lambda invoked")

    states = get_alarm_states()

    signals = {
        "app": states.get("app-health-alarm") == "ALARM",
        "cpu": states.get("cpu-high-alarm") == "ALARM"
    }

    confidence = sum(signals.values())

    if signals["app"]:
        incident_id = "app-health-alarm"
    elif signals["cpu"]:
        incident_id = "cpu-high-alarm"
    else:
        incident_id = "none"

    if incident_id != "none":
        count, cooldown = record_incident(incident_id)
    else:
        count, cooldown = 0, False

    # ---------- Decision Logic ----------

    if confidence == 0:
        decision = "OBSERVE"

    elif confidence == 1:
        if count >= 2 and cooldown:
            decision = "SUPPRESS"

        elif count == 3:
            decision = "RESTART_APP"
            restart_app()

        elif count >= 4:
            decision = "REBOOT_EC2"
            reboot_instance()

        else:
            decision = "WARN"

    else:
        decision = "REMEDIATE"

    result = {
        "signals": signals,
        "confidence": confidence,
        "decision": decision,
        "incident_count": count,
        "cooldown": cooldown
    }

    print(result)
    return result


