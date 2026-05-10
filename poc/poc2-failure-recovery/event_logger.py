import pika
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def connect():
    for _ in range(20):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        except Exception:
            time.sleep(3)
    raise RuntimeError("Cannot connect to RabbitMQ")

conn = connect()
ch = conn.channel()
ch.queue_declare(queue="sandbox_events")

def on_message(ch, method, props, body):
    event = json.loads(body)
    print(f"[EVENT] {event['event']:25s} sandbox={event['sandbox']}", flush=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)

ch.basic_consume(queue="sandbox_events", on_message_callback=on_message)
print("Waiting for events...")
ch.start_consuming()