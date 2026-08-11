package callpython

import "testing"

func TestResolvePythonExecutable_PrefersEnvVarOverBarePATHLookup(t *testing.T) {
	t.Setenv("BRAGS_PYTHON_EXECUTABLE", "/some/venv/bin/python3")

	got := ResolvePythonExecutable()
	if got != "/some/venv/bin/python3" {
		t.Fatalf("expected env var value, got %q", got)
	}
}

func TestResolvePythonExecutable_FallsBackToBarePython3WhenUnset(t *testing.T) {
	t.Setenv("BRAGS_PYTHON_EXECUTABLE", "")

	got := ResolvePythonExecutable()
	if got != "python3" {
		t.Fatalf("expected fallback \"python3\", got %q", got)
	}
}
