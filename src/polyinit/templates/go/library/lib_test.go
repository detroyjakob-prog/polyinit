package {{package_name}}

import "testing"

func TestGreet(t *testing.T) {
	result := Greet("Alice")
	if result != "Hello Alice from {{project_name}}!" {
		t.Errorf("got %s", result)
	}
}
