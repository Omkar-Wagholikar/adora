package main

import (
	"log"

	callpython "goHalf/callPython"

	"github.com/fsnotify/fsnotify"
)

func main() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()

	dirToWatch := "/home/omkar/rag_check/watched"

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

			switch {
			case event.Op&fsnotify.Create == fsnotify.Create:
				log.Printf("File created: %s\n", event.Name)
			case event.Op&fsnotify.Write == fsnotify.Write:
				log.Printf("File modified: %s\n", event.Name)
			case event.Op&fsnotify.Remove == fsnotify.Remove:
				log.Printf("File deleted: %s\n", event.Name)
			case event.Op&fsnotify.Rename == fsnotify.Rename:
				log.Printf("File renamed: %s\n", event.Name)
			case event.Op&fsnotify.Chmod == fsnotify.Chmod:
				log.Printf("File permissions changed: %s\n", event.Name)
			}

			callpython.CallPython(dirToWatch+"/test.py", make([]string, 0))

		case err, ok := <-watcher.Errors:
			if !ok {
				return
			}
			log.Println("Error:", err)
		}
	}
}
