package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func get(t *testing.T, path string) (int, map[string]string) {
	t.Helper()

	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodGet, path, nil)
	newRouter().ServeHTTP(recorder, request)

	var body map[string]string
	if err := json.Unmarshal(recorder.Body.Bytes(), &body); err != nil {
		t.Fatalf("GET %s: invalid JSON: %v", path, err)
	}

	return recorder.Code, body
}

func TestRootReturnsGreeting(t *testing.T) {
	status, body := get(t, "/")

	if status != http.StatusOK {
		t.Errorf("GET / status = %d, want %d", status, http.StatusOK)
	}
	if body["message"] != "Hello from {{project_name}}!" {
		t.Errorf("GET / message = %q", body["message"])
	}
}

func TestHealthzReturnsOK(t *testing.T) {
	status, body := get(t, "/healthz")

	if status != http.StatusOK {
		t.Errorf("GET /healthz status = %d, want %d", status, http.StatusOK)
	}
	if body["status"] != "ok" {
		t.Errorf("GET /healthz status body = %q", body["status"])
	}
}