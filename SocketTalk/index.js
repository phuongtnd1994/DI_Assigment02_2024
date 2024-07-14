const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const config = require("./config/config.js");
const { Server } = require("socket.io");
const http = require("http");

const { Client } = require("pg");

const client = new Client({
  user: config.PG_CONFIG.user,
  host: config.PG_CONFIG.host,
  database: config.PG_CONFIG.database,
  password: config.PG_CONFIG.password,
  port: config.PG_CONFIG.port,
});

client
  .connect()
  .then(() => console.log("Connected to PostgreSQL"))
  .catch((err) => console.error("Connection error", err.stack));

const app = express();

let channel = null;
const sendQueue = "request_queue";
const receiveQueue = "response_queue";

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*",
  },
});

io.on("connection", (socket) => {
  console.log(`socket ${socket.id} connected`);

  socket.on("disconnect", () => {
    console.log("user disconnected");
  });

  socket.on("hello", (socket) => {
    io.emit("rsp", "world");
  });

  socket.on("getProduct", (msg) => {
    console.log(msg);
    regStr = `%${msg.split(" ").join("%")}%`;

    const query = `Select * from products where lower(prd_name) like '${regStr}'`;

    client
      .query(query)
      .then((res) => {
        // console.log(res.rows);
        io.emit("rsp", res.rows);
      })
      .catch((err) => {
        io.emit("rsp", err.stack);
      });
  });

  socket.on("getInfo", (msg) => {
    console.log(msg);

    regStr = msg.split(" ").join(", ");

    const query = `Select * from products where id in (${regStr})`;

    client
      .query(query)
      .then((res) => {
        data = res.rows;
        channel.sendToQueue(sendQueue, Buffer.from(JSON.stringify(data)));

        io.emit("rsp", `sent ${regStr} to crawlers`);
      })
      .catch((err) => {
        io.emit("rsp", err.stack);
      });
  });
});

/* Rabbit mq */
const amqp = require("amqplib");
const opt = {
  credentials: amqp.credentials.plain(
    config.RABBIT_CONFIG.username,
    config.RABBIT_CONFIG.password
  ),
};

const rburl = `amqp://${config.RABBIT_CONFIG.host}:${config.RABBIT_CONFIG.port}`;

(async () => {
  try {
    const conn = await amqp.connect(rburl, opt);

    console.log("Connected to rabbitmq");

    channel = await conn.createChannel();
    // const channel2 = await conn.createChannel();

    await channel.assertQueue(sendQueue, { durable: false });

    await channel.assertQueue(receiveQueue, { durable: false });

    channel.consume(receiveQueue, (msg) => {
      if (msg !== null) {
        const receivedMessage = msg.content.toString();
        console.log(receivedMessage);
      }
    });
  } catch (error) {
    console.error("Error:", error);
  }
})();

const PORT = config.PORT_SERVER;

server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
