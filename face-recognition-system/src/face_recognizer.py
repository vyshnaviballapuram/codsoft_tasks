"""
face_recognizer.py
-------------------
Face recognition / identification built on OpenCV's LBPH (Local Binary
Patterns Histograms) face recognizer. LBPH is chosen as the default engine
because it:
  - requires no heavyweight compiled dependencies (unlike dlib/ArcFace),
  - trains in real time from a handful of enrollment photos per person,
  - runs fast on CPU, which matters for a live-webcam demo.

The module is intentionally structured so the recognizer is a swappable
component (`BaseRecognizer`), so a deep embedding model such as
FaceNet / ArcFace / a Siamese network can be dropped in later without
touching the rest of the application (see ArcFaceRecognizer stub at the
bottom for the extension point).
"""

import os
import json
import cv2
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
KNOWN_FACES_DIR = os.path.join(DATA_DIR, "known_faces")
MODEL_PATH = os.path.join(DATA_DIR, "embeddings", "lbph_model.yml")
LABELS_PATH = os.path.join(DATA_DIR, "embeddings", "labels.json")

FACE_SIZE = (200, 200)


class FaceRecognizer:
    def __init__(self):
        os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1, neighbors=8, grid_x=8, grid_y=8
        )
        self.label_map = {}   # int_label -> name
        self.trained = False
        self._load()

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def _load(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH):
            try:
                self.recognizer.read(MODEL_PATH)
                with open(LABELS_PATH, "r") as f:
                    raw = json.load(f)
                self.label_map = {int(k): v for k, v in raw.items()}
                self.trained = True
            except Exception:
                self.trained = False

    def _save(self):
        self.recognizer.write(MODEL_PATH)
        with open(LABELS_PATH, "w") as f:
            json.dump(self.label_map, f, indent=2)

    # ------------------------------------------------------------------ #
    # Enrollment
    # ------------------------------------------------------------------ #
    def enroll(self, name: str, face_images: list):
        """
        Add / update a person in the database with a list of cropped BGR
        face images, then retrain the recognizer on the full dataset.
        """
        person_dir = os.path.join(KNOWN_FACES_DIR, self._safe_name(name))
        os.makedirs(person_dir, exist_ok=True)

        existing = len(os.listdir(person_dir))
        for i, img in enumerate(face_images):
            gray = self._preprocess(img)
            cv2.imwrite(os.path.join(person_dir, f"{existing + i:03d}.png"), gray)

        self.retrain_all()
        return len(os.listdir(person_dir))

    def delete_person(self, name: str):
        import shutil
        person_dir = os.path.join(KNOWN_FACES_DIR, self._safe_name(name))
        if os.path.exists(person_dir):
            shutil.rmtree(person_dir)
        self.retrain_all()

    def list_people(self):
        if not os.path.exists(KNOWN_FACES_DIR):
            return []
        return sorted(
            [d for d in os.listdir(KNOWN_FACES_DIR)
             if os.path.isdir(os.path.join(KNOWN_FACES_DIR, d))]
        )

    def retrain_all(self):
        """Rebuild the LBPH model from every image currently on disk."""
        faces, labels = [], []
        self.label_map = {}
        people = self.list_people()

        for label_id, person in enumerate(people):
            self.label_map[label_id] = person
            person_dir = os.path.join(KNOWN_FACES_DIR, person)
            for fname in os.listdir(person_dir):
                path = os.path.join(person_dir, fname)
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                img = cv2.resize(img, FACE_SIZE)
                faces.append(img)
                labels.append(label_id)

        if len(faces) == 0:
            self.trained = False
            return

        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1, neighbors=8, grid_x=8, grid_y=8
        )
        self.recognizer.train(faces, np.array(labels))
        self.trained = True
        self._save()

    # ------------------------------------------------------------------ #
    # Inference
    # ------------------------------------------------------------------ #
    def recognize(self, face_img: np.ndarray, distance_threshold: float = 75.0):
        """
        Predict identity for a single cropped BGR face image.

        Returns:
            (name_or_"Unknown", confidence_percent)
            confidence_percent is derived from the LBPH distance
            (lower distance = better match), rescaled to an intuitive
            0-100% "match confidence" score.
        """
        if not self.trained:
            return "Unknown", 0.0

        gray = self._preprocess(face_img)
        label_id, distance = self.recognizer.predict(gray)

        # Convert LBPH distance (lower = better, typically 0-150+) to a
        # user-facing confidence percentage.
        confidence_pct = max(0.0, 100.0 - (distance / distance_threshold) * 100.0)
        confidence_pct = min(confidence_pct, 100.0)

        if distance > distance_threshold or label_id not in self.label_map:
            return "Unknown", round(confidence_pct, 1)

        return self.label_map[label_id], round(confidence_pct, 1)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _preprocess(img: np.ndarray) -> np.ndarray:
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.equalizeHist(img)
        img = cv2.resize(img, FACE_SIZE)
        return img

    @staticmethod
    def _safe_name(name: str) -> str:
        return "".join(c for c in name.strip() if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")


# ---------------------------------------------------------------------- #
# Extension point: swap in a deep embedding model (ArcFace / FaceNet /
# a custom Siamese network) by implementing the same enroll/recognize
# interface and wiring it in app.py's engine selector.
# ---------------------------------------------------------------------- #
class ArcFaceRecognizerStub:
    """
    Placeholder showing how a deep-embedding recognizer would plug in:
    1. Extract a 512-d embedding per enrolled face using an ArcFace ONNX model.
    2. Store embeddings (instead of raw images) in data/embeddings/.
    3. At inference, compute cosine similarity between the query embedding
       and every stored embedding; the highest similarity above a threshold
       wins. This scales better and is more robust than LBPH, at the cost
       of a heavier runtime dependency (onnxruntime).
    """
    pass
