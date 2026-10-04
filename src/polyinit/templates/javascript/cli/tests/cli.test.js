import test from "node:test";
import assert from "node:assert";
import { main, parseArgs } from "../src/index.js";

test("parseArgs handles defaults", () => {
  const args = parseArgs(["node", "index.js"]);
  assert.strictEqual(args.name, undefined);
});

test("main returns 0 and prints greeting", () => {
  const originalLog = console.log;
  let output = "";
  console.log = (msg) => {
    output = msg;
  };
  try {
    assert.strictEqual(main(["node", "index.js", "--name", "Alice"]), 0);
    assert.strictEqual(output, "Hello Alice from {{project_name}}!");
  } finally {
    console.log = originalLog;
  }
});