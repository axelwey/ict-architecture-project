const amqp = require("amqplib");

const QUEUE = "flag.submitted";
const RABBITMQ_URL = process.env.RABBITMQ_URL || "amqp://guest:guest@rabbitmq:5672";
const DELAY_MS = 5000;

// in-memory opslag (in productie: echte database)
const progress = {};

async function connectRabbitMQ() {
  for (let i = 1; i <= 10; i++) {
    try {
      const connection = await amqp.connect(RABBITMQ_URL);
      const channel = await connection.createChannel();
      await channel.assertQueue(QUEUE, { durable: true });
      channel.prefetch(1);
      console.log("[consumer] verbonden met RabbitMQ, wacht op events...");
      return channel;
    } catch (err) {
      console.log(`[consumer] poging ${i}/10 mislukt, wacht 3s...`);
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
  throw new Error("kan RabbitMQ niet bereiken");
}

async function verwerkEvent(event) {
  const { userId, challengeId, correct, timestamp } = event;

  console.log(`[consumer] event ontvangen: ${userId} → ${challengeId}`);
  console.log(`[consumer] wacht ${DELAY_MS / 1000}s (simuleert DB-write)...`);
  await new Promise((r) => setTimeout(r, DELAY_MS));

  if (!progress[userId]) progress[userId] = {};
  progress[userId][challengeId] = {
    correct,
    lastAttempt: timestamp,
    attempts: (progress[userId][challengeId]?.attempts ?? 0) + 1,
  };

  const opgelost = Object.values(progress[userId]).filter((c) => c.correct).length;
  console.log(`[consumer] voortgang bijgewerkt: ${userId} heeft ${opgelost} challenge(s) opgelost`);
}

async function start() {
  const channel = await connectRabbitMQ();

  channel.consume(QUEUE, async (msg) => {
    if (!msg) return;
    const event = JSON.parse(msg.content.toString());
    await verwerkEvent(event);
    channel.ack(msg);
  });
}

start();
