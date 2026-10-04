package main

import "testing"

func TestGreet(t *testing.T) {
	if got, want := greet("Alice"), "Hello Alice from {{project_name}}!"; got != want {
		t.Errorf("greet(%q) = %q, want %q", "Alice", got, want)
	}
}

func TestGreetDefaultsToWorld(t *testing.T) {
	if got, want := greet(""), "Hello World from {{project_name}}!"; got != want {
		t.Errorf("greet(%q) = %q, want %q", "", got, want)
	}
}