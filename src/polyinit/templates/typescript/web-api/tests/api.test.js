import test from "node:test";
import assert from "node:assert";
import { app } from "../dist/index.js";

test("GET / returns greeting", async () => {
  const server = app.listen(0);
  try {
    const port = server.address().port;
    const res = await fetch(`http://localhost:${port}/`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.message, "Hello from {{project_name}}!");
  } finally {
    server.close();
  }
});

test("GET /healthz returns ok", async () => {
  const server = app.listen(0);
  try {
    const port = server.address().port;
    const res = await fetch(`http://localhost:${port}/healthz`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.deepStrictEqual(data, { status: "ok" });
  } finally {
    server.close();
  }
});