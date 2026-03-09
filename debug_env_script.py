import sys
import os

try:
    import groq
    res = "Groq IMPORTED"
except ImportError:
    res = "Groq NOT FOUND"

with open("debug_env.txt", "w") as f:
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"Python Path: {sys.path}\n")
    f.write(f"Result: {res}\n")
