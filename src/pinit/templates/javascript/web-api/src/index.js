import express from "express";

const app = express();
const port = process.env.PORT || 3000;

app.get("/", (req, res) => {
  res.json({ message: "Hello from {{project_name}}!" });
});

app.get("/healthz", (req, res) => {
  res.json({ status: "ok" });
});

function startServer() {
  const server = app.listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
  });
  return server;
}

if (import.meta.url === new URL(process.argv[1], "file:").href) {
  startServer();
}

export { app, startServer };