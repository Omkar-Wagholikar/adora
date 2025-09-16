package main

/*
#include <stdlib.h>
*/
import "C"

import (
	cronFileWatcher "goHalf/cronFileWatcher"
	persistentFileWatcher "goHalf/persistentFileWatcher"
	"os"

	log "github.com/sirupsen/logrus"
)

func init() {
	log.SetLevel(log.InfoLevel)
	log.SetFormatter(&log.TextFormatter{FullTimestamp: true})
	file, err := os.OpenFile("/home/omkar/rag_check/go_filewatcher.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err == nil {
		log.SetOutput(file)
	} else {
		log.Warn("Failed to log to file, using default stderr")
	}
}

//export StartCronWatcher
func StartCronWatcher() {
	log.Info("Go: Starting Cron Watcher...")
	cronFileWatcher.FileWatcher()
}

//export StartPersistentWatcher
func StartPersistentWatcher(cpath *C.char) {
	path := C.GoString(cpath)
	log.Infof("Go: Starting Persistent Watcher at %s", path)
	persistentFileWatcher.FileWatcher(path)
}

func main() {}
