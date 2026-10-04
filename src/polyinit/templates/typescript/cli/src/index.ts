#!/usr/bin/env node

export function parseArgs(argv: string[]): { name?: string } {
  const args: { name?: string } = {};
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

export function main(argv: string[] = process.argv): number {
  const { name = "World" } = parseArgs(argv);
  console.log(`Hello ${name} from {{project_name}}!`);
  return 0;
}

if (import.meta.url === new URL(process.argv[1], "file:").href) {
  main();
}