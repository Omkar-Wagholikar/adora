package server

import (
	"goHalf/utils"
	"io"
	"log"
	"net/http"
	"os/exec"
	"sync"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// Allow connections from any origin (for development)
		// In production, you should validate the origin
		return true
	},
}

func HandleWS(w http.ResponseWriter, r *http.Request) {
	utils.SetUpLogs()
	log.Println("Inside websocket")

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Upgrade error:", err)
		return
	}
	defer conn.Close()

	// Create a mutex to synchronize writes to the WebSocket
	var writeMutex sync.Mutex

	// Start Python subprocess (REPL)
	cmd := exec.Command("python3", "-m", "brags", "query") // interactive
	stdin, err := cmd.StdinPipe()
	if err != nil {
		log.Println("Failed to create stdin pipe:", err)
		return
	}

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		log.Println("Failed to create stdout pipe:", err)
		return
	}

	stderr, err := cmd.StderrPipe()
	if err != nil {
		log.Println("Failed to create stderr pipe:", err)
		return
	}

	if err := cmd.Start(); err != nil {
		log.Println("Failed to start Python:", err)
		return
	}

	// Create a channel to handle graceful shutdown
	done := make(chan struct{})

	// Pipe Python stdout to WebSocket (with mutex protection)
	go streamOutput(stdout, conn, &writeMutex, "stdout", done)
	// Pipe Python stderr to WebSocket (with mutex protection)
	go streamOutput(stderr, conn, &writeMutex, "stderr", done)

	// Read from WebSocket and send to Python stdin
	go func() {
		defer close(done) // Signal other goroutines to stop
		for {
			_, msg, err := conn.ReadMessage()
			if err != nil {
				log.Println("WS read error:", err)
				break
			}

			// Write the command to Python stdin
			if _, err := stdin.Write(msg); err != nil {
				log.Println("Failed to write to Python stdin:", err)
				break
			}
			if _, err := stdin.Write([]byte("\n")); err != nil {
				log.Println("Failed to write newline to Python stdin:", err)
				break
			}
		}
	}()

	// Wait for the WebSocket reading goroutine to finish
	<-done

	// Clean up
	stdin.Close()
	if cmd.Process != nil {
		cmd.Process.Kill()
	}
	cmd.Wait() // Wait for the process to actually terminate
}

func streamOutput(pipe io.ReadCloser, conn *websocket.Conn, mutex *sync.Mutex, source string, done <-chan struct{}) {
	utils.SetUpLogs()
	log.Println("Inside streamOutput")
	defer pipe.Close()

	buf := make([]byte, 1024)
	for {
		select {
		case <-done:
			return
		default:
			// Set a read timeout to prevent blocking indefinitely
			n, err := pipe.Read(buf)
			if n > 0 {
				// Use mutex to prevent concurrent writes to WebSocket
				mutex.Lock()
				writeErr := conn.WriteMessage(websocket.TextMessage, buf[:n])
				mutex.Unlock()

				if writeErr != nil {
					log.Printf("Failed to write %s to WebSocket: %v", source, writeErr)
					return
				}
			}
			if err != nil {
				if err != io.EOF {
					log.Printf("Error reading from %s: %v", source, err)
				}
				return
			}
		}
	}
}
