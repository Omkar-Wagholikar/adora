package cronFileWatcher

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sync"
	"time"

	callpython "goHalf/callPython"

	"github.com/robfig/cron/v3"
	log "github.com/sirupsen/logrus"
)

// WatchFunc defines the function signature for watch operations
type WatchFunc func(path string)

// CronScheduler manages cron jobs with dependency injection
type CronScheduler struct {
	cronJobs map[string]*cron.Cron
	mu       sync.RWMutex
}

// NewCronScheduler creates a new cron scheduler
func NewCronScheduler() *CronScheduler {
	return &CronScheduler{
		cronJobs: make(map[string]*cron.Cron),
	}
}

// StartCronWatcher starts a cron job with dependency injection
func (cs *CronScheduler) StartCronWatcher(path string, period int, watchFunc WatchFunc, mapping map[string]time.Time) {

	cs.mu.Lock()
	defer cs.mu.Unlock()
	log.Println("StartCronWatcher accquired lock")

	// Stop existing job if it exists
	if existingCron, exists := cs.cronJobs[path]; exists {
		existingCron.Stop()
	}

	// Create new cron with seconds support
	c := cron.New(cron.WithSeconds())
	// var mapping map[string]time.Time

	spec := fmt.Sprintf("@every %ds", period)
	log.Infof("Creating cron job for path %s with spec: %s", path, spec)

	// Add the job with injected function
	_, err := c.AddFunc(spec, func() {
		log.Infof("[Cron for %s] Running started", path)

		// Get current file states
		vals := listFiles(path, "*.pdf")
		if mapping == nil {
			mapping = vals
			log.Infof("[Cron for %s] Initial mapping created with %d files", path, len(mapping))
			return
		}

		// Check for changes
		for k, v := range vals {
			value, exists := mapping[k]
			if !exists {
				log.Infof("New file detected: %s", k)
				mapping[k] = v
				watchFunc(k) // Call the injected function
			} else if value.Before(v) {
				log.Infof("File updated: %s", k)
				mapping[k] = v
				watchFunc(k) // Call the injected function
			}
		}

		log.Infof("[Cron for %s] Running complete", path)
	})

	if err != nil {
		log.Errorf("Failed to add cron job for path %s: %v", path, err)
		return
	}

	c.Start()
	cs.cronJobs[path] = c
	log.Infof("Cron scheduler started for path: %s", path)
	log.Println("StartCronWatcher released lock")
}

// StopCronWatcher stops a specific cron job
func (cs *CronScheduler) StopCronWatcher(path string) {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	if cronJob, exists := cs.cronJobs[path]; exists {
		cronJob.Stop()
		delete(cs.cronJobs, path)
		log.Infof("Stopped cron job for path: %s", path)
	}
}

// StopAll stops all cron jobs
func (cs *CronScheduler) StopAll() {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	for path, cronJob := range cs.cronJobs {
		cronJob.Stop()
		log.Infof("Stopped cron job for path: %s", path)
	}
	cs.cronJobs = make(map[string]*cron.Cron)
}

// ExecuteFileWatch is a standalone function that can be used as a WatchFunc
func ExecuteFileWatch(path string) {
	log.Infof("Executing file watch for: %s", path)

	// Check if the file exists and get its info
	fileInfo, err := os.Stat(path)
	if err != nil {
		if os.IsNotExist(err) {
			// File was removed
			log.Infof("File removed: %s", path)
			callpython.PerformFileOp("REMOVE", path)
		} else {
			log.Errorf("Error getting file info for %s: %v", path, err)
		}
		return
	}

	log.Infof("File modified: %s (size: %d bytes, modified: %s)",
		path, fileInfo.Size(), fileInfo.ModTime().Format(time.RFC3339))

	callpython.PerformFileOp("WRITE", path)
}

func listFiles(dir string, pattern string) map[string]time.Time {
	mapping := make(map[string]time.Time)

	err := filepath.WalkDir(dir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			log.Warnf("Error accessing path %s: %v", path, err)
			return nil // Continue walking
		}

		if d.IsDir() {
			return nil
		}

		match, err := filepath.Match(pattern, d.Name())
		if err != nil {
			log.Warnf("Error matching pattern for file %s: %v", d.Name(), err)
			return nil
		}

		if match {
			fileInfo, err := os.Stat(path)
			if err != nil {
				if os.IsNotExist(err) {
					log.Warnf("File '%s' does not exist", path)
				} else {
					log.Warnf("Error getting file info for '%s': %v", path, err)
				}
				return nil
			}

			lastModified := fileInfo.ModTime()
			mapping[path] = lastModified
		}
		return nil
	})

	if err != nil {
		log.Errorf("Error walking directory %s: %v", dir, err)
		return nil
	}

	return mapping
}
