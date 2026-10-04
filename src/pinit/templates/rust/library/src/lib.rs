/// Greets the given name.
pub fn greet(name: &str) -> String {
    format!("Hello {} from {{project_name}}!", name)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        assert_eq!(greet("Alice"), "Hello Alice from {{project_name}}!");
    }
}