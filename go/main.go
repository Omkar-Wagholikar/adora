package main

import (
	// persistentFileWatcher "goHalf/persistentFileWatcher"
	cronFileWatcher "goHalf/cronFileWatcher"

	log "github.com/sirupsen/logrus"
)

func init() {
	log.SetLevel(log.InfoLevel)
	log.SetFormatter(&log.TextFormatter{FullTimestamp: true})
}

func main() {
	cronFileWatcher.FileWatcher()
	// persistentFileWatcher.FileWatcher("/home/omkar/rag_check/watched")
}
