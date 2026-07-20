"""
utils.py
--------
Shared helpers: bounding-box drawing, color coding, and small formatting
utilities used across the Streamlit app.
"""

import cv2
import numpy as np

KNOWN_COLOR = (46, 204, 113)     # green (BGR)  -> recognized identity
UNKNOWN_COLOR = (66, 133, 244)   # blue/orange-ish (BGR) -> unknown face


def draw_annotations(frame: np.ndarray, detections: list, labels: list = None):
    """
    Draw bounding boxes + labels on a frame.

    Args:
        frame: BGR image (modified in place and returned).
        detections: list of {"box": (x,y,w,h), "confidence": float}
        labels: optional list of (name, recognition_confidence) tuples,
                same length/order as detections. If None, only the
                detector confidence is shown.
    """
    for i, det in enumerate(detections):
        x, y, w, h = det["box"]
        det_conf = det["confidence"]

        if labels is not None and i < len(labels):
            name, rec_conf = labels[i]
            color = KNOWN_COLOR if name != "Unknown" else UNKNOWN_COLOR
            text = f"{name}  {rec_conf:.0f}%"
        else:
            color = UNKNOWN_COLOR
            text = f"Face {det_conf*100:.0f}%"

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # label background
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        label_y = max(y - 10, th + 4)
        cv2.rectangle(frame, (x, label_y - th - 8), (x + tw + 8, label_y + 2), color, -1)
        cv2.putText(
            frame, text, (x + 4, label_y - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA
        )

    return frame


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
