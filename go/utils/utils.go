package utils

import (
	"os"

	log "github.com/sirupsen/logrus"
)

func SetUpLogs() {
	log.SetLevel(log.InfoLevel)
	log.SetFormatter(&log.TextFormatter{
		FullTimestamp: true,
		DisableQuote:  true,
	})
	file, err := os.OpenFile("/home/omkar/rag_check/go_filewatcher.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err == nil {
		log.SetOutput(file)
	} else {
		log.Warn("Failed to log to file, using default stderr")
	}
}
