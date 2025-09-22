package main

import (
	"encoding/json"
	"fmt"
	"goHalf/server"
	"goHalf/utils"
	"net/http"
	"os"
	"strconv"
	"time"

	watchermanager "goHalf/watcherManager"

	log "github.com/sirupsen/logrus"
)

func main() {
	utils.SetUpLogs()

	// Create watcher manager with 30-second update interval
	watcherManager := watchermanager.NewWatcherManager(3 * time.Second)

	// Load existing watchers
	if err := watcherManager.LoadWatchers(); err != nil {
		log.Println("ActiveJobs directory may be corrupted, exiting")
		log.Print(err.Error())
		os.Exit(1)
	}

	// Start periodic updates
	watcherManager.Start()

	// Initialize all existing jobs
	watcherManager.InitializeAllJobs()

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

		watcher := server.WatchEntry{
			GivenPath:   path,
			WatcherType: wtype,
			Period:      int64(period),
			LastUpdate:  make(map[string]time.Time),
		}

		// Add to manager and initialize
		watcherManager.AddWatcher(watcher)
		watcherManager.InitializeJob(watcher)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(watcher)
	})

	http.HandleFunc("/list_watchers", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		watchers := watcherManager.GetWatchers()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(watchers)
	})

	fmt.Println("Server running at http://localhost:8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
