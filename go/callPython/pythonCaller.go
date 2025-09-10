package callpython

import (
	"log"
)

func PerformFileOp(event_type string, file_path string) {
	log.Println("PerformFileOp:\t" + event_type + "\t" + file_path)
	// val := strings.Join(args, " ")
	// cmd := exec.Command("python3", filePath, val)
	// output, err := cmd.CombinedOutput()
	// if err != nil {
	// 	log.Printf("Error calling Python: %v\nOutput: %s", err, output)
	// } else {
	// 	log.Printf("Python output: %s", output)
	// }
}
