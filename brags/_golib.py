# import os
# import sys
# import ctypes
# from pathlib import Path

# def load_go_library():
#     base_dir = Path(__file__).parent / "bin"

#     if sys.platform.startswith("linux"):
#         lib_path = base_dir / "libbrags.so"
#     else:
#         raise RuntimeError(f"Unsupported platform: {sys.platform}")

#     if not lib_path.exists():
#         err = f"Go library not found: {lib_path}"
#         raise FileNotFoundError(err)

#     return ctypes.CDLL(str(lib_path))

# go_lib = load_go_library()
