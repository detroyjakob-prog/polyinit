package {{package_name}}

func Greet(name string) string {
	if name == "" {
		name = "World"
	}
	return "Hello " + name + " from {{project_name}}!"
}
