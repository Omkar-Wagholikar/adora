import os
import sys
import ctypes
from pathlib import Path

def load_go_library():
    base_dir = Path(__file__).parent / "bin"

    if sys.platform.startswith("linux"):
        lib_path = base_dir / "filewatcher_linux_amd64.so"
    elif sys.platform == "darwin":
        if sys.maxsize > 2**32 and "arm" in os.uname().machine:
            lib_path = base_dir / "filewatcher_darwin_arm64.dylib"
        else:
            lib_path = base_dir / "filewatcher_darwin_amd64.dylib"
    elif sys.platform == "win32":
        lib_path = base_dir / "filewatcher_windows_amd64.dll"
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

    if not lib_path.exists():
        raise FileNotFoundError(f"Go library not found: {lib_path}")

    return ctypes.CDLL(str(lib_path))

go_lib = load_go_library()
