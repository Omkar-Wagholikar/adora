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

func PerformFileOp(event_type string, file_path string) {
	python_file_path, err := resolvePythonScriptPath()
	if err != nil {
		log.Printf("PerformFileOp: failed to resolve vector_store_updater.py path: %v", err)
		return
	}

	log.Println("PerformFileOp:\t" + event_type + "\t" + file_path)
	cmd := exec.Command("python3", python_file_path, event_type, file_path)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error calling Python: %v\nOutput: %s", err, output)
	} else {
		log.Printf("Python output: %s", output)
	}
}
