package utils

import (
	"os"
	"path/filepath"

	log "github.com/sirupsen/logrus"
)

func SetUpLogs() {
	log.SetLevel(log.InfoLevel)
	log.SetFormatter(&log.TextFormatter{
		FullTimestamp: true,
		DisableQuote:  true,
	})

	// Log next to the running executable rather than a machine-specific
	// absolute path, so the binary works regardless of who built/installed it.
	logPath := "go_filewatcher.log"
	if exePath, err := os.Executable(); err == nil {
		logPath = filepath.Join(filepath.Dir(exePath), "go_filewatcher.log")
	}

	file, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err == nil {
		log.SetOutput(file)
	} else {
		log.Warn("Failed to log to file, using default stderr")
	}
}
