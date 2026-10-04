export function greet(name = "World") {
  return `Hello ${name} from {{project_name}}!`;
}

export function version() {
  return "0.1.0";
}