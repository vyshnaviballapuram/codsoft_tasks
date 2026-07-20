# VisionID — Face Detection & Recognition System

A full-stack computer vision application that detects faces in images, video,
and live webcam feeds using a deep-learning detector, and recognizes enrolled
identities in real time. Built for the CodSoft AI Internship "Face Detection
and Recognition" task, with a production-style architecture rather than a
single notebook script.

---

## Features

- **Deep-learning face detection** — OpenCV DNN module running a Caffe SSD
  detector on a ResNet-10 backbone (trained on WIDER FACE). A classic Haar
  cascade engine is included as a selectable baseline for comparison.
- **Face recognition** — LBPH (Local Binary Patterns Histogram) classifier,
  trained live from a handful of enrollment photos per person. Architected
  behind a clean `enroll()` / `recognize()` interface so it can be swapped
  for a deep embedding model (ArcFace / FaceNet / a Siamese network) without
  touching the rest of the app.
- **Multi-input pipeline** — image upload, video upload (frame-by-frame
  processing with a progress bar and downloadable annotated output), and
  webcam capture.
- **Identity management** — enroll new people from uploaded photos or a
  webcam capture, view a live gallery, and delete identities; the recognizer
  retrains automatically.
- **Professional web UI** — a custom-themed Streamlit interface (dark,
  data/biometric-console aesthetic) instead of a bare demo page, with
  live metrics, a results table, and downloadable outputs.
- **Standalone CLI demo** — `webcam_demo.py` for a native, high-FPS OpenCV
  video loop outside the browser.

---

## Architecture

```
Input (image / video / webcam)
        │
        ▼
1. Face Detection        OpenCV DNN — SSD / ResNet-10        (src/face_detector.py)
        │                 or Haar Cascade (classic baseline)
        ▼
2. Preprocessing          crop + margin, grayscale,
                           histogram equalization, resize
        ▼
3. Face Recognition       LBPH classifier                    (src/face_recognizer.py)
        │
        ▼
   Annotated output + identity + confidence score
```

The Streamlit app (`app.py`) is a thin orchestration layer over
`src/face_detector.py` and `src/face_recognizer.py` — both are plain,
UI-agnostic Python modules that are independently testable and reusable
(e.g. from the CLI script, a batch script, or a future API).

---

## Project structure

```
face_recognition_app/
├── app.py                  # Streamlit web application (main entry point)
├── webcam_demo.py           # Standalone CLI live-webcam demo
├── requirements.txt
├── models/                  # Pretrained DNN face detector (Caffe SSD)
│   ├── deploy.prototxt
│   └── res10_300x300_ssd_iter_140000.caffemodel
├── src/
│   ├── face_detector.py     # Detection engines (DNN + Haar)
│   ├── face_recognizer.py   # LBPH enrollment / recognition + extension point
│   └── utils.py             # Drawing / annotation helpers
└── data/
    ├── known_faces/         # Enrolled face photos, one folder per person
    └── embeddings/          # Serialized trained recognizer model
```

---

## Getting started

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the web app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

For a native high-FPS webcam loop instead of the browser-based capture:

```bash
python webcam_demo.py
```

---

## Usage

1. **Register Identity** — enter a name, upload 3–5 clear photos (or use the
   webcam), and enroll. The app auto-detects and crops the face from each
   photo before training.
2. **Detect — Image / Video / Webcam** — upload a file or take a snapshot;
   detected faces are boxed, and any recognized identity is labeled with a
   match-confidence score.
3. **Manage Database** — review or delete enrolled identities.
4. Tune the **detector confidence threshold** and **match strictness** in
   the sidebar to balance false positives vs. missed detections.

---

## Design notes / why LBPH by default

Deep embedding models (ArcFace, FaceNet) give better accuracy at scale, but
typically depend on `dlib` or `onnxruntime` plus large pretrained weight
downloads, which is fragile in constrained or offline environments. LBPH:

- has zero heavy native build dependencies (ships with `opencv-contrib-python`),
- trains in real time from a small number of enrollment photos,
- is fast enough for a live demo on CPU only.

`src/face_recognizer.py` isolates the recognition logic behind a single
interface specifically so LBPH can be swapped for an ArcFace/FaceNet
embedding-and-cosine-similarity engine, or a Siamese verification network,
as a contained upgrade — see the `ArcFaceRecognizerStub` docstring in that
file for the intended extension path.

## Known limitations

- LBPH is texture-based, not a learned embedding — accuracy degrades faster
  than deep methods as the number of enrolled identities grows.
- Detection accuracy drops for extreme angles, heavy occlusion, or very
  small faces (under ~30px), which is inherent to the SSD-ResNet10 model.
- No liveness / anti-spoofing check — this is a recognition demo, not a
  hardened authentication system.

## Tech stack

`Python` · `OpenCV (DNN + LBPH)` · `Streamlit` · `NumPy` · `Pandas` · `Pillow`
