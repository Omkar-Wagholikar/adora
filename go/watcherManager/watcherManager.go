package watchermanager

import (
	"bufio"
	"encoding/json"
	"fmt"
	"goHalf/server"
	"os"
	"sync"
	"time"

	cronFileWatcher "goHalf/cronFileWatcher"
	persistentFileWatcher "goHalf/persistentFileWatcher"

	log "github.com/sirupsen/logrus"
)

// WatcherManager handles the lifecycle of all watchers and periodic updates
type WatcherManager struct {
	activeWatchers []server.WatchEntry
	mu             sync.RWMutex
	cronScheduler  *cronFileWatcher.CronScheduler
	updateInterval time.Duration
}

func NewWatcherManager(updateInterval time.Duration) *WatcherManager {
	return &WatcherManager{
		activeWatchers: make([]server.WatchEntry, 0),
		cronScheduler:  cronFileWatcher.NewCronScheduler(),
		updateInterval: updateInterval,
	}
}

// Start begins the periodic update process
func (wm *WatcherManager) Start() {
	log.Info("Started periodicUpdate routine")
	go wm.periodicUpdate()
}

// periodicUpdate runs every updateInterval and syncs the watcher list to file
func (wm *WatcherManager) periodicUpdate() {
	ticker := time.NewTicker(wm.updateInterval)
	defer ticker.Stop()

	for range ticker.C {
		log.Info("Started periodicUpdate routine")
		if err := wm.syncWatchersToFile(); err != nil {
			log.Errorf("Failed to sync watchers to file: %v", err)
		}
	}
}

// syncWatchersToFile writes current watcher state to a temporary file then atomically replaces the main file
func (wm *WatcherManager) syncWatchersToFile() error {
	wm.mu.RLock()
	defer wm.mu.RUnlock()
	log.Println("syncWatchersToFile accquired lock")

	// Create temporary file
	tempFile, err := os.CreateTemp("/home/omkar/rag_check/brags/brags/bin", "ActiveWatcherList.tmp")
	if err != nil {
		return fmt.Errorf("failed to create temp file: %w", err)
	}
	defer os.Remove(tempFile.Name()) // cleanup on error

	// Write all watchers to temp file
	for _, watcher := range wm.activeWatchers {
		log.Println("Writing activewatchers to temp file")
		log.Println(">", watcher.LastUpdate)
		data, err := json.Marshal(watcher)
		if err != nil {
			tempFile.Close()
			return fmt.Errorf("failed to marshal watcher: %w", err)
		}

		if _, err := tempFile.WriteString(string(data) + "\n"); err != nil {
			tempFile.Close()
			return fmt.Errorf("failed to write to temp file: %w", err)
		}
	}

	if err := tempFile.Close(); err != nil {
		return fmt.Errorf("failed to close temp file: %w", err)
	}

	// Atomically replace the main file
	if err := os.Rename(tempFile.Name(), "ActiveWatcherList"); err != nil {
		return fmt.Errorf("failed to replace main file: %w", err)
	}

	log.Infof("Successfully synced %d watchers to file", len(wm.activeWatchers))
	log.Println("syncWatchersToFile released lock")
	return nil
}

// AddWatcher adds a new watcher to the active list
func (wm *WatcherManager) AddWatcher(watcher server.WatchEntry) {
	wm.mu.Lock()
	defer wm.mu.Unlock()
	wm.activeWatchers = append(wm.activeWatchers, watcher)
}

// GetWatchers returns a copy of all active watchers
func (wm *WatcherManager) GetWatchers() []server.WatchEntry {
	wm.mu.RLock()
	defer wm.mu.RUnlock()
	log.Println("GetWatchers accquired lock")

	result := make([]server.WatchEntry, len(wm.activeWatchers))
	copy(result, wm.activeWatchers)

	log.Println("GetWatchers releasing lock")
	return result
}

// LoadWatchers loads watchers from the file
func (wm *WatcherManager) LoadWatchers() error {
	log.Println("LoadWatchers started")

	watchers, err := ListAllWatchers()
	if err != nil {
		return err
	}

	wm.mu.Lock()
	wm.activeWatchers = watchers
	wm.mu.Unlock()
	log.Println("LoadWatchers ended, loaded", len(wm.activeWatchers), "watchers")
	return nil
}

func AppendWatcherToFile(watcher *server.WatchEntry) error {
	file, err := os.OpenFile("/home/omkar/rag_check/brags/brags/bin/ActiveWatcherList", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer file.Close()

	data, err := json.Marshal(watcher)
	if err != nil {
		return err
	}

	_, err = file.WriteString(string(data) + "\n")
	return err
}

func ListAllWatchers() ([]server.WatchEntry, error) {
	log.Println("ListAllWatchers started")
	log.Println("Getting file")
	file, err := os.Open("./ActiveWatcherList")
	log.Println("Got file")

	if err != nil {
		log.Println("Failed to open or create ActiveWatcherList")
		return nil, err
	}
	log.Println("No error in getting file")

	defer file.Close()

	var watchers []server.WatchEntry
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		var w server.WatchEntry
		if err := json.Unmarshal(scanner.Bytes(), &w); err == nil {
			watchers = append(watchers, w)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}
	log.Println("ListAllWatchers complete, got", len(watchers), "watchers")
	return watchers, nil
}

func (wm *WatcherManager) InitializeJob(entry server.WatchEntry) {
	switch entry.WatcherType {
	case "persistent":
		go StartPersistentWatcher(entry.GivenPath)
	case "cron":
		watchFunc := func(path string) {
			log.Infof("Cron job executed for path: %s", path)
			cronFileWatcher.ExecuteFileWatch(path)
		}
		go wm.cronScheduler.StartCronWatcher(entry.GivenPath, int(entry.Period), watchFunc, entry.LastUpdate)
	default:
		log.Println("Unknown config given, crashing")
		os.Exit(2)
	}
}

func (wm *WatcherManager) InitializeAllJobs() {
	watchers := wm.GetWatchers()
	for _, entry := range watchers {
		wm.InitializeJob(entry)
		log.Printf(">> %s %s %d %v", entry.GivenPath, entry.WatcherType, entry.Period, entry.LastUpdate)
	}
}

//export StartPersistentWatcher
func StartPersistentWatcher(path string) {
	log.Infof("Go: Starting Persistent Watcher at %s", path)
	persistentFileWatcher.FileWatcher(path)
}
