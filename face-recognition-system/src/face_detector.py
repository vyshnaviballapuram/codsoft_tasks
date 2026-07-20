"""
face_detector.py
-----------------
Deep-learning face detection using OpenCV's DNN module (a Caffe-based SSD
detector built on a ResNet-10 backbone). This is the same class of model
family used in production pipelines, and is significantly more robust than
Haar cascades to pose, lighting, and partial occlusion.

A Haar cascade detector is also included as a lightweight fallback / for
side-by-side comparison, since the assignment explicitly mentions it.
"""

import os
import cv2
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

PROTOTXT_PATH = os.path.join(MODEL_DIR, "deploy.prototxt")
CAFFEMODEL_PATH = os.path.join(MODEL_DIR, "res10_300x300_ssd_iter_140000.caffemodel")


class FaceDetector:
    """Unified interface over a DNN (SSD-ResNet10) detector and a Haar cascade detector."""

    def __init__(self, method: str = "dnn", confidence_threshold: float = 0.5):
        """
        Args:
            method: "dnn" (recommended, deep learning) or "haar" (classic, fast).
            confidence_threshold: minimum confidence for DNN detections to be kept.
        """
        self.method = method
        self.confidence_threshold = confidence_threshold

        self._dnn_net = None
        self._haar_cascade = None

        if method == "dnn":
            self._load_dnn()
        elif method == "haar":
            self._load_haar()
        else:
            raise ValueError("method must be 'dnn' or 'haar'")

    # ------------------------------------------------------------------ #
    # Model loading
    # ------------------------------------------------------------------ #
    def _load_dnn(self):
        if not (os.path.exists(PROTOTXT_PATH) and os.path.exists(CAFFEMODEL_PATH)):
            raise FileNotFoundError(
                "DNN face detector model files are missing from the models/ folder."
            )
        self._dnn_net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, CAFFEMODEL_PATH)

    def _load_haar(self):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._haar_cascade = cv2.CascadeClassifier(cascade_path)

    # ------------------------------------------------------------------ #
    # Detection
    # ------------------------------------------------------------------ #
    def detect(self, frame: np.ndarray):
        """
        Detect faces in a BGR image.

        Returns:
            List of dicts: {"box": (x, y, w, h), "confidence": float}
            Boxes are clipped to image bounds.
        """
        if self.method == "dnn":
            return self._detect_dnn(frame)
        return self._detect_haar(frame)

    def _detect_dnn(self, frame: np.ndarray):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )
        self._dnn_net.setInput(blob)
        detections = self._dnn_net.forward()

        results = []
        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            if confidence < self.confidence_threshold:
                continue
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)
            if x2 <= x1 or y2 <= y1:
                continue
            results.append({"box": (x1, y1, x2 - x1, y2 - y1), "confidence": confidence})
        return results

    def _detect_haar(self, frame: np.ndarray):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._haar_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        return [{"box": (int(x), int(y), int(w), int(h)), "confidence": 1.0} for (x, y, w, h) in faces]

    @staticmethod
    def crop_face(frame: np.ndarray, box, margin: float = 0.15):
        """Crop a face region with a small margin, clipped to frame bounds."""
        h_img, w_img = frame.shape[:2]
        x, y, w, h = box
        mx, my = int(w * margin), int(h * margin)
        x1, y1 = max(0, x - mx), max(0, y - my)
        x2, y2 = min(w_img, x + w + mx), min(h_img, y + h + my)
        return frame[y1:y2, x1:x2]
