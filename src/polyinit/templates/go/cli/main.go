package main

import (
	"flag"
	"fmt"
)

// greet builds the greeting printed for the given name.
func greet(name string) string {
	if name == "" {
		name = "World"
	}
	return fmt.Sprintf("Hello %s from {{project_name}}!", name)
}

func main() {
	name := flag.String("name", "World", "name to greet")
	flag.Parse()
	fmt.Println(greet(*name))
}