export function greet(name: string = "World"): string {
  return `Hello ${name} from {{project_name}}!`;
}

export function version(): string {
  return "0.1.0";
}