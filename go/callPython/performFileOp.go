package callpython

import (
	"log"
	"os/exec"
)

func PerformFileOp(event_type string, file_path string) {
	python_file_path := "pythonFiles/vector_store_updater.py"
	log.Println("PerformFileOp:\t" + event_type + "\t" + file_path)
	cmd := exec.Command("python3", python_file_path, event_type, file_path)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error calling Python: %v\nOutput: %s", err, output)
	} else {
		log.Printf("Python output: %s", output)
	}
}
