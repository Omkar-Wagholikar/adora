package main

import (
	"encoding/json"
	"fmt"
	server_datatypes "goHalf/server"
	"goHalf/utils"
	"net/http"
	"os"
	"strconv"
	"time"

	watchermanager "goHalf/watcherManager"

	log "github.com/sirupsen/logrus"
)

type Response struct {
	Message string `json:"message"`
	Status  string `json:"status"`
}

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

	mux := http.NewServeMux()
	server := &http.Server{
		Addr:    ":8011",
		Handler: mux,
	}

	mux.HandleFunc("/add_path", func(w http.ResponseWriter, r *http.Request) {
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

		watcher := server_datatypes.WatchEntry{
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

	mux.HandleFunc("/list_watchers", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		watchers := watcherManager.GetWatchers()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(watchers)
	})

	mux.HandleFunc("/kill", func(w http.ResponseWriter, r *http.Request) {
		// Respond to the client
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(Response{
			Message: "killing server process",
			Status:  "server shutting down",
		})
		log.Println("Received /kill request. Sending shutdown signal...")

		// Initiate the shutdown from a separate goroutine
		go func() {
			// Give the response time to be sent
			time.Sleep(1 * time.Second)
			os.Exit(0)
		}()
	})

	mux.HandleFunc("/ping", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(Response{Message: "pong", Status: "server running normally"})
	})

	fmt.Println("Server running at http://localhost:8011")
	// log.Fatal(http.ListenAndServe(":8011", nil))
	// log.Fatal(http.ListenAndServe(":8011", mux))
	log.Fatal(server.ListenAndServe())
}
