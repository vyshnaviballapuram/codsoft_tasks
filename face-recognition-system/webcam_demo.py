"""
webcam_demo.py
---------------
Standalone script for continuous, real-time face detection + recognition
from a local webcam using OpenCV's native video loop (higher frame rate
than the browser-based snapshot in the Streamlit app).

Run:
    python webcam_demo.py
Press 'q' to quit.
"""

import sys
import os
import time
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from face_detector import FaceDetector
from face_recognizer import FaceRecognizer
from utils import draw_annotations


def main():
    detector = FaceDetector(method="dnn", confidence_threshold=0.5)
    recognizer = FaceRecognizer()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: could not open webcam (index 0).")
        return

    print("VisionID live webcam demo — press 'q' to quit.")
    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = detector.detect(frame)
        labels = None
        if recognizer.trained:
            labels = []
            for det in detections:
                crop = FaceDetector.crop_face(frame, det["box"], margin=0.1)
                if crop.size == 0:
                    labels.append(("Unknown", 0.0))
                    continue
                labels.append(recognizer.recognize(crop))

        annotated = draw_annotations(frame, detections, labels)

        now = time.time()
        fps = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now
        cv2.putText(
            annotated, f"FPS: {fps:.1f}", (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 229, 199), 2
        )

        cv2.imshow("VisionID - Live Face Detection (press 'q' to quit)", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
