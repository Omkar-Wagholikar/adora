package main

import (
	"log"
	"time"

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

	// Debounce state
	// pending holds the most recent event type for each file
	// Example: {"file_path": "WRITE"/"READ"...}
	pending := make(map[string]string) // file -> event type
	// Present Debounce window is 0, this is just to create the timer
	timer := time.NewTimer(0)
	if !timer.Stop() {
		// Reset the timer if it has already fired before
		<-timer.C
	}

	flush := func() {
		for evType, file := range pending {
			log.Printf("Debounced event: %s %s\n", evType, file)
			callpython.PerformFileOp(evType, file)
		}
		pending = make(map[string]string)
	}

	for {
		select {
		case event, ok := <-watcher.Events:
			if !ok {
				return
			}

			evType := ""
			switch {
			case event.Op&fsnotify.Create == fsnotify.Create:
				evType = "CREATE"
			case event.Op&fsnotify.Write == fsnotify.Write:
				evType = "WRITE"
			case event.Op&fsnotify.Remove == fsnotify.Remove:
				evType = "REMOVE"
			case event.Op&fsnotify.Rename == fsnotify.Rename:
				evType = "RENAME"
			}

			if evType != "" {

				// Save/overwrite the latest event for this file
				log.Printf("Queued event: %s %s\n", evType, event.Name)
				pending[event.Name] = evType

				// Reset debounce timer:
				// if another event arrives before it fires,
				// the timer is extended by another 1 second
				timer.Reset(1 * time.Second) // debounce window
			}

		// Timer expired -> no new events for 1s -> flush batch
		case <-timer.C:
			flush()

		// Watcher errors
		case err, ok := <-watcher.Errors:
			if !ok {
				return
			}
			log.Println("Error:", err)
		}
	}
}
