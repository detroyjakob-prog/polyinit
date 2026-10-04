package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type Message struct {
	Message string `json:"message"`
}

type Status struct {
	Status string `json:"status"`
}

// newRouter builds the HTTP routes for the API.
func newRouter() *http.ServeMux {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(Message{Message: "Hello from {{project_name}}!"})
	})
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(Status{Status: "ok"})
	})

	return mux
}

func main() {
	addr := ":3000"
	fmt.Println("Listening on " + addr)
	http.ListenAndServe(addr, newRouter())
}