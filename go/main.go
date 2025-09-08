package main

import (
	"fmt"
	"log"
	"os/exec"

	"github.com/fsnotify/fsnotify"
)

func callPython(path string) {
	cmd := exec.Command("python3", "handler.py", path)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Error calling Python: %v\nOutput: %s", err, output)
	} else {
		log.Printf("Python output: %s", output)
	}
}

func main() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()

	dirToWatch := "./watched"

	err = watcher.Add(dirToWatch)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Watching directory:", dirToWatch)

	for {
		select {
		case event, ok := <-watcher.Events:
			if !ok {
				return
			}
			log.Println("Event:", event)
			fmt.Println(event.Name)
			// if event.Op&(fsnotify.Create|fsnotify.Write|fsnotify.Remove) != 0 {
			//     callPython(event.Name)
			// }

		case err, ok := <-watcher.Errors:
			if !ok {
				return
			}
			log.Println("Error:", err)
		}
	}
}
