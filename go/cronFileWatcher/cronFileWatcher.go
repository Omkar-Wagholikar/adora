package cronFileWatcher

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"time"

	"github.com/robfig/cron/v3"
	log "github.com/sirupsen/logrus"
)

func listFiles(dir string, pattern string) map[string]time.Time {
	var mapping = make(map[string]time.Time)

	err := filepath.WalkDir(dir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		if d.IsDir() {
			return nil
		}

		match, err := filepath.Match(pattern, d.Name())
		if err != nil {
			return err
		}

		if match {

			fileInfo, err := os.Stat(path)
			if err != nil {
				if os.IsNotExist(err) {
					fmt.Printf("File '%s' does not exist.\n", path)
				} else {
					log.Fatalf("Error getting file info for '%s': %v\n", path, err)
				}
			}

			// Get the last modification time
			lastModified := fileInfo.ModTime()
			mapping[path] = lastModified
		}
		return nil
	})
	if err != nil {
		return nil
	}

	return mapping
}

//	sec min hour day month weekday
//
// c.AddFunc("0 * * * * *", func() {})
func FileWatcher() {
	log.Info("Create new cron scheduler")

	// Create new cron (with seconds support)
	c := cron.New(cron.WithSeconds())
	var mapping map[string]time.Time = nil

	// Add jobs
	_, err := c.AddFunc("*/3 * * * * *", func() { // every minute at second 0
		log.Info("[Job 1] Running started")
		vals := listFiles("/home/omkar/rag_check/watched/", "*.txt")
		if mapping == nil {
			mapping = vals
			return
		}

		for k, v := range vals {
			if mapping[k].Compare(v) == -1 { // only tirgger if mapping is older than vals
				mapping[k] = v
				fmt.Println(k + " was updated")
			}
		}
		log.Info("[Job 1] Running complete")
	})
	if err != nil {
		log.Fatal(err)
	}

	c.Start()
	// Block forever
	select {}
}
