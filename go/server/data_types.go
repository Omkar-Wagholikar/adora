package server

import (
	"bytes"
	"encoding/binary"
	"time"
)

type WatchEntry struct {
	GivenPath   string
	WatcherType string
	Period      int64
	LastUpdate  map[string]time.Time
}

func WatchEntrySerializer(w *WatchEntry) ([]byte, error) {
	var buffer bytes.Buffer

	writeString := func(s string) error {
		size := int32(len(s))
		if err := binary.Write(&buffer, binary.BigEndian, size); err != nil {
			return err
		}
		if err := binary.Write(&buffer, binary.BigEndian, []byte(s)); err != nil {
			return err
		}
		return nil
	}

	writeTimeMap := func(m map[string]time.Time) error {
		size := int32(len(m))
		if err := binary.Write(&buffer, binary.BigEndian, size); err != nil {
			return err
		}
		// fmt.Println("Write map size:", size)
		for key, value := range m {
			if err := writeString(key); err != nil {
				return err
			}
			if err := binary.Write(&buffer, binary.BigEndian, value.Unix()); err != nil {
				return err
			}
		}
		return nil
	}

	// Write the fields of the Watcher struct
	if err := writeString(w.GivenPath); err != nil {
		return nil, err
	}
	if err := writeString(w.WatcherType); err != nil {
		return nil, err
	}
	if err := binary.Write(&buffer, binary.BigEndian, w.Period); err != nil {
		return nil, err
	}
	if err := writeTimeMap(w.LastUpdate); err != nil {
		return nil, err
	}

	return buffer.Bytes(), nil
}

func WatchEntryDeserializer(data []byte) (*WatchEntry, error) {
	buffer := bytes.NewReader(data)

	var watcher WatchEntry
	var size int32
	var err error

	readString := func() (string, error) {
		if err := binary.Read(buffer, binary.BigEndian, &size); err != nil {
			return "readString error 1", err
		}
		// fmt.Println("read string key size:", size)
		str := make([]byte, size)
		if err := binary.Read(buffer, binary.BigEndian, &str); err != nil {
			return "readString error 2", err
			// return "", err
		}
		// fmt.Println("read string value size:", string(str))
		return string(str), nil
	}

	readTimeMap := func() (map[string]time.Time, error) {
		var result = make(map[string]time.Time)
		if err := binary.Read(buffer, binary.BigEndian, &size); err != nil {
			return nil, err
		}
		// fmt.Println("read map size: ", size)
		total_size := size
		for i := int32(0); i < total_size; i++ {
			// fmt.Println("read map index:", i)
			key, err := readString()
			if err != nil {
				// fmt.Println("issue in reading key")
				return nil, err
			}
			var unixTime int64
			if err := binary.Read(buffer, binary.BigEndian, &unixTime); err != nil {
				// fmt.Println("Issue in reading time")
				return nil, err
			}
			result[key] = time.Unix(unixTime, 0)
		}
		// fmt.Println("read map complete")
		return result, nil
	}

	if watcher.GivenPath, err = readString(); err != nil {
		return nil, err
	}
	if watcher.WatcherType, err = readString(); err != nil {
		return nil, err
	}
	if err := binary.Read(buffer, binary.BigEndian, &watcher.Period); err != nil {
		return nil, err
	}
	if watcher.LastUpdate, err = readTimeMap(); err != nil {
		return nil, err
	}

	return &watcher, nil
}
