const express = require("express");
const amqp = require("amqplib");
// expres voor HTTP webserver en amqp voor RabbitMQ communicatie

const PORT = 3000;
const QUEUE = "flag.submitted";
const RABBITMQ_URL = process.env.RABBITMQ_URL || "amqp://guest:guest@rabbitmq:5672";

// challenges en hun correcte flags
const FLAGS = {
  "challenge-001": "FLAG{sql_injection_mastered}",
  "challenge-002": "FLAG{xss_reflected_found}",
  "challenge-003": "FLAG{rce_via_deserialization}",
};



async function connectRabbitMQ() {
  //// We proberen maximaal 10 keer te verbinden. Dit is nodig omdat RabbitMQ tijdens het opstarten (in Docker) soms trager is dan dit script.
  for (let i = 1; i <= 10; i++) {
    try {
      const connection = await amqp.connect(RABBITMQ_URL);
      channel = await connection.createChannel();
      await channel.assertQueue(QUEUE, { durable: true });
      console.log("[producer] verbonden met RabbitMQ");
      return;

    } catch (err) {
      console.log(`[producer] poging ${i}/10 mislukt, wacht 3s...`);
      await new Promise((r) => setTimeout(r, 3000));
    }
  }
  throw new Error("kan RabbitMQ niet bereiken");
}

//initialiseer express app
const app = express();
app.use(express.json());

app.post("/submit", (req, res) => {
  const { userId, challengeId, flag } = req.body;

  if (!userId || !challengeId || !flag) {
    return res.status(400).json({ error: "userId, challengeId en flag zijn verplicht" });
  }

  const correct = FLAGS[challengeId] === flag.trim();
  const timestamp = new Date().toISOString();

  console.log(`[producer] ${userId} → ${challengeId} | correct: ${correct}`);

  // stuur direct antwoord terug aan de student
  res.json({ correct, timestamp });

  // publiceer event naar RabbitMQ NADAT het antwoord verstuurd is
  channel.sendToQueue(
    QUEUE,
    Buffer.from(JSON.stringify({ userId, challengeId, correct, timestamp })),
    { persistent: true }
  );
  console.log(`[producer] event gepubliceerd op queue '${QUEUE}'`);
});

app.get("/health", (_req, res) => res.json({ status: "ok" }));

connectRabbitMQ().then(() => {
  app.listen(PORT, () => console.log(`[producer] luistert op :${PORT}`));
});
