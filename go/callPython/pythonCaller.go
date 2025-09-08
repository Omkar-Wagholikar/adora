package callpython

import (
	"log"
	"os/exec"
	"strings"
)

func CallPython(filePath string, args []string) {
	val := strings.Join(args, " ")
	cmd := exec.Command("python3", filePath, val)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error calling Python: %v\nOutput: %s", err, output)
	} else {
		log.Printf("Python output: %s", output)
	}
}
