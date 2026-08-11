package callpython

import (
	"log"
	"os"
	"os/exec"
	"path/filepath"
)

// resolvePythonScriptPath locates vector_store_updater.py next to the
// running executable (build.sh copies pythonFiles/ alongside the built
// binary), so this works regardless of which machine or directory the
// server was built/installed on.
func resolvePythonScriptPath() (string, error) {
	exePath, err := os.Executable()
	if err != nil {
		return "", err
	}
	return filepath.Join(filepath.Dir(exePath), "pythonFiles", "vector_store_updater.py"), nil
}

// ResolvePythonExecutable prefers BRAGS_PYTHON_EXECUTABLE (set by
// brags/utils/server.py's spawn_server() to sys.executable) over a bare
// "python3" PATH lookup -- whatever "python3" resolves to first on PATH may
// not be the interpreter brags is actually installed into (a venv, --user
// install, pipx, etc.), which silently broke every file-change event with a
// ModuleNotFoundError for brags. Falls back to "python3" (not "python" --
// PEP 394 only guarantees "python3" exists; a bare "python" symlink is
// common but not universal, e.g. plain Debian/Ubuntu without
// python-is-python3 installed) so running a python interpreter directly,
// outside `brags init`/`brags watch`, still works as before. Exported so
// go/server/handleWS.go's own python subprocess (the web UI's query relay)
// shares the same resolution instead of hardcoding "python" independently.
func ResolvePythonExecutable() string {
	if exe := os.Getenv("BRAGS_PYTHON_EXECUTABLE"); exe != "" {
		return exe
	}
	return "python3"
}

func PerformFileOp(event_type string, file_path string) {
	python_file_path, err := resolvePythonScriptPath()
	if err != nil {
		log.Printf("PerformFileOp: failed to resolve vector_store_updater.py path: %v", err)
		return
	}

	log.Println("PerformFileOp:\t" + event_type + "\t" + file_path)
	cmd := exec.Command(ResolvePythonExecutable(), python_file_path, event_type, file_path)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error calling Python: %v\nOutput: %s", err, output)
	} else {
		log.Printf("Python output: %s", output)
	}
}
