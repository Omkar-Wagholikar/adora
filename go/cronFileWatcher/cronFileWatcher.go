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

// CronScheduler manages cron jobs with dependency injection.
//
// lastUpdates holds the per-path "file -> last-seen mtime" state that each
// cron job reads and mutates on every tick. It is owned exclusively by
// CronScheduler and guarded by mu: earlier this state was a bare
// map[string]time.Time handed to the cron closure by reference *and* shared
// directly with WatcherManager.activeWatchers for persistence, so the cron
// goroutine's writes and WatcherManager's periodic JSON-marshal reads could
// race on the same Go map with no synchronization between them at all
// (fatal error: concurrent map iteration and map write). Keeping the map
// here means every access goes through mu, and callers outside this package
// only ever see a defensive copy via GetLastUpdate.
type CronScheduler struct {
	cronJobs    map[string]*cron.Cron
	lastUpdates map[string]map[string]time.Time
	mu          sync.RWMutex
}

// NewCronScheduler creates a new cron scheduler
func NewCronScheduler() *CronScheduler {
	return &CronScheduler{
		cronJobs:    make(map[string]*cron.Cron),
		lastUpdates: make(map[string]map[string]time.Time),
	}
}

// GetLastUpdate returns a snapshot copy of the current file->mtime state for
// a watched path, safe to marshal/persist from another goroutine.
func (cs *CronScheduler) GetLastUpdate(path string) map[string]time.Time {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	src := cs.lastUpdates[path]
	out := make(map[string]time.Time, len(src))
	for k, v := range src {
		out[k] = v
	}
	return out
}

// StartCronWatcher starts a cron job with dependency injection
func (cs *CronScheduler) StartCronWatcher(path string, period int, watchFunc WatchFunc, initial map[string]time.Time) {

	cs.mu.Lock()
	log.Println("StartCronWatcher accquired lock")

	// Stop existing job if it exists
	if existingCron, exists := cs.cronJobs[path]; exists {
		existingCron.Stop()
	}

	// Seed this scheduler's own copy of the last-known file state; the
	// caller's map is never retained or mutated beyond this point.
	seeded := make(map[string]time.Time, len(initial))
	for k, v := range initial {
		seeded[k] = v
	}
	cs.lastUpdates[path] = seeded

	// Create new cron with seconds support
	c := cron.New(cron.WithSeconds())

	spec := fmt.Sprintf("@every %ds", period)
	log.Infof("Creating cron job for path %s with spec: %s", path, spec)

	// Add the job with injected function
	_, err := c.AddFunc(spec, func() {
		log.Infof("[Cron for %s] Running started", path)

		// Get current file states
		vals := listFiles(path, "*.pdf")

		cs.mu.Lock()
		mapping := cs.lastUpdates[path]
		if mapping == nil {
			mapping = make(map[string]time.Time)
			cs.lastUpdates[path] = mapping
		}
		if len(mapping) == 0 {
			for k, v := range vals {
				mapping[k] = v
			}
			cs.mu.Unlock()
			log.Infof("[Cron for %s] Initial mapping created with %d files", path, len(vals))
			return
		}

		// Check for changes, collecting callbacks to run after releasing the lock
		var changed []string
		for k, v := range vals {
			value, exists := mapping[k]
			if !exists {
				log.Infof("New file detected: %s", k)
				mapping[k] = v
				changed = append(changed, k)
			} else if value.Before(v) {
				log.Infof("File updated: %s", k)
				mapping[k] = v
				changed = append(changed, k)
			}
		}
		cs.mu.Unlock()

		for _, k := range changed {
			watchFunc(k) // Call the injected function outside the lock
		}

		log.Infof("[Cron for %s] Running complete", path)
	})

	if err != nil {
		cs.mu.Unlock()
		log.Errorf("Failed to add cron job for path %s: %v", path, err)
		return
	}

	c.Start()
	cs.cronJobs[path] = c
	cs.mu.Unlock()
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
