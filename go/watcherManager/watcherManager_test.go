package watchermanager

import "testing"

// Regression test: a missing ActiveWatcherList file is the normal state on
// a fresh install (nothing has ever called syncWatchersToFile() yet), not a
// corruption error -- main.go used to os.Exit(1) whenever ListAllWatchers
// returned any error at all, so treating "file doesn't exist" the same as a
// real read error meant the server could never start for the first time
// without a human manually pre-creating an empty file first.
func TestListAllWatchers_MissingFileIsNotAnError(t *testing.T) {
	t.Chdir(t.TempDir())

	watchers, err := ListAllWatchers()
	if err != nil {
		t.Fatalf("expected no error when ActiveWatcherList doesn't exist yet, got: %v", err)
	}
	if len(watchers) != 0 {
		t.Fatalf("expected zero watchers, got %d", len(watchers))
	}
}
