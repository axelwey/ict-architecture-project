import docker
import pika
import json
import time
import threading
import logging
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logging.getLogger("pika").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

client = docker.DockerClient(base_url="unix://var/run/docker.sock", version="auto")
app = Flask(__name__)

active = {} 


def publish(event: str, sandbox: str):
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", retry_delay=2, connection_attempts=5))
        ch = conn.channel()
        ch.queue_declare(queue="sandbox_events")
        ch.basic_publish(exchange="", routing_key="sandbox_events", body=json.dumps({"event": event, "sandbox": sandbox}))
        conn.close()
        log.info("Published: %s for %s", event, sandbox)
    except Exception as e:
        log.error("RabbitMQ error: %s", e)


def start_sandbox(name: str):
    container = client.containers.run(
        "alpine", ["sh", "-c", "while true; do sleep 5; done"],
        detach=True,
        labels={"managed_by": "provisioner", "sandbox_name": name},
    )
    active[name] = container
    publish("sandbox.started", name)
    log.info("Started %s (%s)", name, container.short_id)
    return container


def poll_sandboxes():
    """Poll elke 3 seconden of sandboxen nog draaien."""
    while True:
        time.sleep(3)
        for name, container in list(active.items()):
            try:
                container.reload()
                status = container.status
                if status != "running":
                    log.warning("CRASH detected: %s is %s", name, status)
                    publish("sandbox.crashed", name)
                    time.sleep(1)
                    log.info("Recovering %s...", name)
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass
                    start_sandbox(name)
                    publish("sandbox.recovered", name)
            except Exception as e:
                log.error("Error checking %s: %s", name, e)


@app.route("/status")
def status():
    result = {}
    for name, c in active.items():
        try:
            c.reload()
            result[name] = {"id": c.short_id, "state": c.status}
        except Exception:
            result[name] = {"state": "unknown"}
    return jsonify(result)


if __name__ == "__main__":
    time.sleep(3)

    for name in ["sandbox-a", "sandbox-b", "sandbox-c"]:
        start_sandbox(name)

    threading.Thread(target=poll_sandboxes, daemon=True).start()

    log.info("Provisioner ready.")
    app.run(host="0.0.0.0", port=5000)