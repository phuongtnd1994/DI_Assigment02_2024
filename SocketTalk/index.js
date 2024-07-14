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

  socket.on("getInfo", (msg) => {});
});

const PORT = config.PORT_SERVER;

server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
