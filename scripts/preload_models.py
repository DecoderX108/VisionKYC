"""Download the ML model weights at Docker build time.

Without this, the first request after starting the container would have to
download ~700 MB (VGG-Face, Facenet, EasyOCR) before it could answer.
"""
import tensorflow as tf  # noqa: F401  (must be imported before deepface)
from deepface import DeepFace
import easyocr

print("Preloading EasyOCR (en)...", flush=True)
easyocr.Reader(["en"], gpu=False)

for name in ("VGG-Face", "Facenet"):  # verify() default model, represent() model
    print(f"Preloading DeepFace model {name}...", flush=True)
    DeepFace.build_model(name)

print("All models preloaded.", flush=True)
