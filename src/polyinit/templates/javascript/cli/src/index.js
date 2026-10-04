#!/usr/bin/env node

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--name" || arg === "-n") {
      args.name = argv[i + 1] || "World";
      i++;
    } else if (arg.startsWith("--name=")) {
      args.name = arg.slice("--name=".length);
    }
  }
  return args;
}

function main(argv = process.argv) {
  const { name = "World" } = parseArgs(argv);
  console.log(`Hello ${name} from {{project_name}}!`);
  return 0;
}

main();

export { main, parseArgs };