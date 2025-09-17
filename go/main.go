package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"goHalf/server"
	"goHalf/utils"
	"net/http"
	"os"
	"strconv"
	"time"

	cronFileWatcher "goHalf/cronFileWatcher"
	persistentFileWatcher "goHalf/persistentFileWatcher"

	log "github.com/sirupsen/logrus"
)

func AppendWatcherToFile(watcher *server.WatchEntry) error {
	file, err := os.OpenFile("ActiveWatcherList", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
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
	file, err := os.Open("ActiveWatcherList")
	if err != nil {
		return nil, err
	}
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
	return watchers, nil
}

func InitializeJob(job server.WatchEntry) {
	switch job.WatcherType {
	case "persistent":
		// spawn a go routine
		go StartPersistentWatcher(job.GivenPath)
	case "cron":
		// spawn a go routine
		go StartCronWatcher(job.GivenPath, int(job.Period))
	default:
		log.Println("Unknown config given crashing")
		os.Exit(2)
	}
}

func InitializeAllJobs(active_jobs []server.WatchEntry) {
	for _, entry := range active_jobs {
		InitializeJob(entry)
		log.Printf("%s %s %d %v", entry.GivenPath, entry.WatcherType, entry.Period, entry.LastUpdate)

	}
}

//export StartCronWatcher
func StartCronWatcher(path string, period int) {
	log.Info("Go: Starting Cron Watcher...")
	cronFileWatcher.FileWatcher(path, period)
}

//export StartPersistentWatcher
func StartPersistentWatcher(path string) {
	log.Infof("Go: Starting Persistent Watcher at %s", path)
	persistentFileWatcher.FileWatcher(path)
}

func main() {
	utils.SetUpLogs()
	active_jobs, err := ListAllWatchers()
	if err != nil {
		log.Println("ActiveJobs directory may be corruted exiting")
		log.Print(err.Error())
		os.Exit(1)
	}

	InitializeAllJobs(active_jobs)

	http.HandleFunc("/add_path", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		query := r.URL.Query()
		path := query.Get("path")
		wtype := query.Get("type")
		periodStr := query.Get("period")

		period, err := strconv.Atoi(periodStr)
		if err != nil {
			http.Error(w, "Invalid period: "+err.Error(), http.StatusBadRequest)
			return
		}

		watcher := &server.WatchEntry{
			GivenPath:   path,
			WatcherType: wtype,
			Period:      int64(period),
			LastUpdate:  make(map[string]time.Time),
		}

		InitializeJob(*watcher)

		if err := AppendWatcherToFile(watcher); err != nil {
			http.Error(w, "Failed to write to file: "+err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(watcher)
	})

	http.HandleFunc("/list_watchers", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		watchers, err := ListAllWatchers()
		if err != nil {
			http.Error(w, "Failed to read watchers: "+err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(watchers)
	})

	fmt.Println("Server running at http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
