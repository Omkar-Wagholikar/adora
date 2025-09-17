import os
import logging
import threading
from ._golib import go_lib

# module-level state
_watcher_started = False

def _start_watcher():
    global _watcher_started
    if _watcher_started:
        return  # already running

    def _run():
        try:
            go_lib.StartCronWatcher()
        except Exception as e:
            logging.warning(f"Go watcher failed: {e}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    _watcher_started = True

if not os.environ.get("BRAGS_SKIP_INIT"):
    _start_watcher()
