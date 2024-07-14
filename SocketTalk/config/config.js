const PORT_SERVER = 8888;

const PG_CONFIG = {
  user: "postgres",
  host: "127.0.0.1",
  database: "postgres",
  password: "postgres",
  port: 5400,
};

const RABBIT_CONFIG = {
  host: "127.0.0.1",
  port: "5672",
  username: "user",
  password: "password",
};

module.exports = {
  PORT_SERVER,
  PG_CONFIG,
  RABBIT_CONFIG,
};
