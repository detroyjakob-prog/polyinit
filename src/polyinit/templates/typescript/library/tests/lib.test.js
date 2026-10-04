import test from "node:test";
import assert from "node:assert";
import { greet, version } from "../dist/index.js";

test("greet returns greeting", () => {
  assert.strictEqual(greet("Alice"), "Hello Alice from {{project_name}}!");
  assert.strictEqual(greet(), "Hello World from {{project_name}}!");
});

test("version is 0.1.0", () => {
  assert.strictEqual(version(), "0.1.0");
});