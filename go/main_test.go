package main

import (
	"fmt"
	"goHalf/server"
	"testing"
	"time"
)

func timeRoughlyEqual(t1, t2 time.Time) bool {
	// Round both times to the nearest second
	time_diff := t1.Round(time.Second).Sub(t2.Round(time.Second))
	if time_diff > 2 || time_diff < -2 {
		return false
	}
	return true
	// return t1.Round(time.Second).Equal(t2.Round(time.Second))
}

func TestSerialization(t *testing.T) {
	watcher := &server.WatchEntry{
		GivenPath:   "/some/path",
		WatcherType: "Persi",
		Period:      60,
		LastUpdate: map[string]time.Time{
			"file1": time.Now(),
			"file2": time.Now().Add(-time.Hour),
		},
	}

	serializedData, err := server.WatchEntrySerializer(watcher)
	fmt.Println("serializedData: ->> " + string(serializedData) + " <<-")
	if err != nil {
		t.Fatalf("Error serializing watcher: %v", err)
	}

	time.Sleep(3 * time.Second)
	deserializedWatcher, err := server.WatchEntryDeserializer(serializedData)
	if err != nil {
		t.Fatalf("Error deserializing watcher 2: %v", err)
	}

	if deserializedWatcher.GivenPath != watcher.GivenPath {
		t.Errorf("Expected GivenPath %v, but got %v", watcher.GivenPath, deserializedWatcher.GivenPath)
	}

	if deserializedWatcher.WatcherType != watcher.WatcherType {
		t.Errorf("Expected WatcherType %v, but got %v", watcher.WatcherType, deserializedWatcher.WatcherType)
	}

	if deserializedWatcher.Period != watcher.Period {
		t.Errorf("Expected Period %v, but got %v", watcher.Period, deserializedWatcher.Period)
	}

	for key, origTime := range watcher.LastUpdate {
		deserializedTime, exists := deserializedWatcher.LastUpdate[key]
		if !exists {
			t.Errorf("Key %v not found in deserialized LastUpdate map", key)
		}
		if !timeRoughlyEqual(origTime, deserializedTime) {
			t.Errorf("Expected LastUpdate[%v] %v, but got %v", key, origTime, deserializedTime)
		}
	}
}

func TestEmptyWatcher(t *testing.T) {
	watcher := &server.WatchEntry{
		GivenPath:   "",
		WatcherType: "",
		Period:      0,
		LastUpdate:  make(map[string]time.Time),
	}

	serializedData, err := server.WatchEntrySerializer(watcher)
	if err != nil {
		t.Fatalf("Error serializing empty watcher: %v", err)
	}

	deserializedWatcher, err := server.WatchEntryDeserializer(serializedData)
	if err != nil {
		t.Fatalf("Error deserializing empty watcher: %v", err)
	}

	if deserializedWatcher.GivenPath != watcher.GivenPath {
		t.Errorf("Expected GivenPath %v, but got %v", watcher.GivenPath, deserializedWatcher.GivenPath)
	}

	if deserializedWatcher.WatcherType != watcher.WatcherType {
		t.Errorf("Expected WatcherType %v, but got %v", watcher.WatcherType, deserializedWatcher.WatcherType)
	}

	if deserializedWatcher.Period != watcher.Period {
		t.Errorf("Expected Period %v, but got %v", watcher.Period, deserializedWatcher.Period)
	}

	if len(deserializedWatcher.LastUpdate) != 0 {
		t.Errorf("Expected empty LastUpdate map, but got %v", deserializedWatcher.LastUpdate)
	}
}

func TestSerializationConsistency(t *testing.T) {
	now := time.Now()
	watcher := &server.WatchEntry{
		GivenPath:   "/path/to/file",
		WatcherType: "File",
		Period:      100,
		LastUpdate: map[string]time.Time{
			"file1": now,
		},
	}

	serializedData, err := server.WatchEntrySerializer(watcher)
	if err != nil {
		t.Fatalf("Error serializing watcher: %v", err)
	}

	deserializedWatcher, err := server.WatchEntryDeserializer(serializedData)
	if err != nil {
		t.Fatalf("Error deserializing watcher 1: %v", err)
	}

	if !timeRoughlyEqual(deserializedWatcher.LastUpdate["file1"], watcher.LastUpdate["file1"]) {
		t.Errorf("Expected LastUpdate[file1] %v, but got %v", watcher.LastUpdate["file1"], deserializedWatcher.LastUpdate["file1"])
	}
}

func TestInvalidData(t *testing.T) {
	invalidData := []byte{0x00, 0x01, 0x02}

	_, err := server.WatchEntryDeserializer(invalidData)
	if err == nil {
		t.Errorf("Expected error during deserialization, but got nil")
	}
}
