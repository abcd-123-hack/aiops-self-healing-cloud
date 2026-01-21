🤖 AIOps — Self-Healing Cloud Infrastructure

Enterprise-Grade Event-Driven Reliability System

🧱 Architecture
CloudWatch Alarms
        |
        ▼
EventBridge
 (State Change Events)
        |
        ▼
Lambda — Decision Brain
 (Correlation + Logic)
        |
        ▼
DynamoDB
 (Incident Memory)
        |
        ▼
AWS SSM
 (RunCommand)
        |
        ▼
EC2 Instance
 (Self-Healing Actions)

⚙️ Technology Stack
Layer	Technology
Cloud	AWS
Compute	EC2
Monitoring	CloudWatch
Event Bus	EventBridge
Decision Engine	AWS Lambda
Incident Memory	DynamoDB
Remediation	AWS Systems Manager (SSM)
Application	Flask (Python)
📦 Repository Structure
aiops-self-healing-cloud/
│
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── lambda/
│   └── lambda_function.py
│
├── cloudwatch/
│   └── alarms.md
│
├── architecture/
│   └── architecture.png
│
├── screenshots/
│   ├── lambda_logs.png
│   ├── dynamodb_table.png
│   └── cloudwatch_alarm.png
│
└── README.md

🧠 What This System Does

This project implements a real AIOps-style self-healing system that:

Detects failures in real time

Correlates multiple signals

Remembers past incidents

Suppresses alert noise

Automatically heals infrastructure

This is not basic automation — it is stateful operational intelligence.

🔍 Detection Layer

The system monitors:

Application health via custom Flask endpoint

Infrastructure health via CPU metrics

CloudWatch alarms:

app-health-alarm

cpu-high-alarm

These alarms emit state change events.

🧠 Decision Layer (Lambda)

Lambda acts as the brain of the system.

It:

Reads alarm states

Correlates signals

Computes confidence

Queries incident history

Decides what action to take

Sample output:

{
  "signals": {"app": true, "cpu": false},
  "confidence": 1,
  "decision": "SUPPRESS",
  "incident_count": 4,
  "cooldown": true
}

🗄️ Incident Memory (DynamoDB)

The system stores every incident:

Field	Purpose
incident_id	Alarm name
last_seen	Timestamp
count	Number of occurrences

This enables:

Historical context

Alert suppression

Progressive escalation

⏳ Cooldown Suppression

Repeated incidents within a time window are automatically suppressed.

This prevents:

Alert fatigue

Noise

Unnecessary remediation

Real-world SRE tools behave exactly like this.

🔁 Progressive Remediation Strategy

The system heals itself gradually and safely.

Incident Count	Action
1	WARN
2	SUPPRESS
3	Restart Application
4	Reboot EC2 Instance

Remediation is executed using AWS Systems Manager (SSM)
(no SSH, no keys, no human login).

🛠️ Self-Healing Actions
Restart Application
pkill app.py
python3 app.py &

Reboot Instance
sudo reboot


These commands are executed remotely via:

AWS SSM RunCommand
