"""
VisionID — Face Detection & Recognition System
================================================
A resume-grade computer vision application combining:
  - Deep-learning face detection (OpenCV DNN / SSD-ResNet10), with a
    classic Haar-cascade engine available for comparison.
  - Face recognition / identity verification (LBPH), architected so a
    deep embedding model (ArcFace / FaceNet / a Siamese network) can be
    swapped in as a drop-in engine (see src/face_recognizer.py).

Run with:
    streamlit run app.py
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import cv2
import streamlit as st
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from face_detector import FaceDetector          # noqa: E402
from face_recognizer import FaceRecognizer, KNOWN_FACES_DIR  # noqa: E402
from utils import draw_annotations, bgr_to_rgb  # noqa: E402


# ============================================================================
# PAGE CONFIG + THEME
# ============================================================================
st.set_page_config(
    page_title="VisionID · Face Detection & Recognition",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root{
    --bg: #0B0E14;
    --panel: #10141D;
    --panel-2: #151B26;
    --line: #212938;
    --cyan: #00E5C7;
    --cyan-dim: rgba(0,229,199,0.12);
    --amber: #FFB454;
    --text: #E7ECF3;
    --text-dim: #8A93A6;
}

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }
h1, h2, h3, .display-font { font-family: 'Space Grotesk', sans-serif; }
code, .mono { font-family: 'JetBrains Mono', monospace; }

/* Hide default streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

/* Hero */
.vid-hero {
    border: 1px solid var(--line);
    background: linear-gradient(135deg, var(--panel) 0%, var(--panel-2) 100%);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}
.vid-hero::before{
    content:"";
    position:absolute; inset:0;
    background-image:
        linear-gradient(var(--line) 1px, transparent 1px),
        linear-gradient(90deg, var(--line) 1px, transparent 1px);
    background-size: 26px 26px;
    opacity: 0.18;
    pointer-events:none;
}
.vid-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    color: var(--cyan);
    letter-spacing: 3px;
    font-size: 12px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.vid-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 36px;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.vid-sub {
    color: var(--text-dim);
    font-size: 15px;
    max-width: 640px;
    line-height: 1.55;
}

/* Reticle corners (signature element) */
.reticle { position: relative; padding: 4px; }
.reticle::before, .reticle::after,
.reticle .c3, .reticle .c4 { display:none; }

/* Metric cards */
.vid-card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 16px 18px;
    height: 100%;
}
.vid-metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 6px;
}
.vid-metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--cyan);
}

/* Section header w/ corner brackets - the signature motif */
.vid-section {
    font-family: 'JetBrains Mono', monospace;
    color: var(--text);
    font-size: 13px;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-left: 2px solid var(--cyan);
    padding: 4px 0 4px 12px;
    margin: 22px 0 14px 0;
}

/* Pills / badges */
.badge-known {
    background: rgba(46,204,113,0.15); color: #2ECC71;
    border: 1px solid rgba(46,204,113,0.4);
    padding: 2px 10px; border-radius: 20px; font-size: 12px;
    font-family: 'JetBrains Mono', monospace; display:inline-block;
}
.badge-unknown {
    background: rgba(255,180,84,0.15); color: var(--amber);
    border: 1px solid rgba(255,180,84,0.4);
    padding: 2px 10px; border-radius: 20px; font-size: 12px;
    font-family: 'JetBrains Mono', monospace; display:inline-block;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--panel);
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Buttons */
.stButton>button {
    background: var(--cyan-dim);
    color: var(--cyan);
    border: 1px solid var(--cyan);
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.5px;
}
.stButton>button:hover {
    background: var(--cyan);
    color: #06111A;
}
.stDownloadButton>button {
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
}

hr { border-color: var(--line); }

.vid-footer {
    color: var(--text-dim);
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
    padding: 24px 0 8px 0;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# CACHED RESOURCES
# ============================================================================
@st.cache_resource(show_spinner=False)
def load_detector(method: str, conf: float):
    return FaceDetector(method=method, confidence_threshold=conf)


@st.cache_resource(show_spinner=False)
def load_recognizer():
    return FaceRecognizer()


def get_recognizer() -> FaceRecognizer:
    # We manage retraining ourselves, so keep one instance in session_state
    # rather than relying purely on cache_resource (which can't be
    # invalidated per-user easily).
    if "recognizer" not in st.session_state:
        st.session_state.recognizer = FaceRecognizer()
    return st.session_state.recognizer


# ============================================================================
# SIDEBAR — NAVIGATION + SETTINGS
# ============================================================================
with st.sidebar:
    st.markdown(
        "<div style='font-family:Space Grotesk; font-size:22px; font-weight:700; "
        "color:#E7ECF3; margin-bottom:2px;'>◎ VisionID</div>"
        "<div style='font-family:JetBrains Mono; font-size:11px; color:#00E5C7; "
        "letter-spacing:2px; margin-bottom:20px;'>FACE DETECTION SYSTEM</div>",
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        [
            "🏠 Overview",
            "🖼️ Detect — Image",
            "🎞️ Detect — Video",
            "📸 Detect — Webcam",
            "➕ Register Identity",
            "🗂️ Manage Database",
            "ℹ️ Architecture",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("<div class='vid-section' style='margin-top:0;'>DETECTOR SETTINGS</div>", unsafe_allow_html=True)
    detector_method = st.selectbox(
        "Detection engine",
        ["dnn", "haar"],
        format_func=lambda x: "Deep Learning (SSD-ResNet10)" if x == "dnn" else "Haar Cascade (classic)",
    )
    det_confidence = st.slider("Detector confidence threshold", 0.1, 0.95, 0.5, 0.05)

    st.markdown("<div class='vid-section'>RECOGNITION SETTINGS</div>", unsafe_allow_html=True)
    rec_threshold = st.slider("Match strictness (lower = stricter)", 40, 120, 75, 5)

    st.markdown("---")
    recognizer_preview = get_recognizer()
    st.markdown(
        f"<div class='mono' style='font-size:12px; color:#8A93A6;'>"
        f"Registered identities: <span style='color:#00E5C7;'>{len(recognizer_preview.list_people())}</span><br>"
        f"Model status: <span style='color:{'#2ECC71' if recognizer_preview.trained else '#FFB454'};'>"
        f"{'TRAINED' if recognizer_preview.trained else 'EMPTY'}</span></div>",
        unsafe_allow_html=True,
    )

detector = load_detector(detector_method, det_confidence)
recognizer = get_recognizer()


def run_pipeline(frame_bgr: np.ndarray, recognize: bool = True):
    """Detect faces, optionally recognize each, return (annotated_frame, results)."""
    t0 = time.time()
    detections = detector.detect(frame_bgr)
    labels = None
    results = []

    if recognize and recognizer.trained:
        labels = []
        for det in detections:
            crop = FaceDetector.crop_face(frame_bgr, det["box"], margin=0.1)
            if crop.size == 0:
                labels.append(("Unknown", 0.0))
                continue
            name, conf = recognizer.recognize(crop, distance_threshold=rec_threshold)
            labels.append((name, conf))

    for i, det in enumerate(detections):
        entry = {
            "Face #": i + 1,
            "Detector confidence": f"{det['confidence']*100:.1f}%",
            "Identity": labels[i][0] if labels else "—",
            "Match confidence": f"{labels[i][1]:.1f}%" if labels else "—",
        }
        results.append(entry)

    annotated = draw_annotations(frame_bgr.copy(), detections, labels)
    elapsed_ms = (time.time() - t0) * 1000
    return annotated, results, elapsed_ms, detections


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================
if page == "🏠 Overview":
    st.markdown(
        """
        <div class="vid-hero">
            <div class="vid-eyebrow">COMPUTER VISION · BIOMETRICS</div>
            <div class="vid-title">Face Detection &amp; Recognition System</div>
            <div class="vid-sub">
                Detects faces in images, video, and live webcam feeds using a deep-learning
                SSD detector, then identifies enrolled individuals in real time. Built with
                OpenCV, and architected so the recognition engine can be upgraded to a deep
                embedding model (ArcFace / FaceNet / Siamese network) without touching the
                application layer.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    people = recognizer.list_people()
    total_imgs = sum(
        len(os.listdir(os.path.join(KNOWN_FACES_DIR, p))) for p in people
    ) if people else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value in zip(
        [c1, c2, c3, c4],
        ["Registered Identities", "Enrollment Photos", "Detector Engine", "Recognition Engine"],
        [len(people), total_imgs, "SSD-ResNet10" if detector_method == "dnn" else "Haar Cascade", "LBPH"],
    ):
        with col:
            st.markdown(
                f"<div class='vid-card'><div class='vid-metric-label'>{label}</div>"
                f"<div class='vid-metric-value'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='vid-section'>QUICK START</div>", unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown(
            "**1 · Register faces**\n\nGo to *Register Identity* and capture "
            "3–5 photos per person to build the recognition database."
        )
    with q2:
        st.markdown(
            "**2 · Run detection**\n\nUpload an image/video, or use your webcam, "
            "to detect and identify faces in real time."
        )
    with q3:
        st.markdown(
            "**3 · Tune & inspect**\n\nAdjust detector confidence and match "
            "strictness in the sidebar to balance precision vs. recall."
        )

    if people:
        st.markdown("<div class='vid-section'>REGISTERED IDENTITIES</div>", unsafe_allow_html=True)
        cols = st.columns(6)
        for i, p in enumerate(people):
            person_dir = os.path.join(KNOWN_FACES_DIR, p)
            imgs = os.listdir(person_dir)
            with cols[i % 6]:
                if imgs:
                    thumb = cv2.imread(os.path.join(person_dir, imgs[0]))
                    st.image(thumb, caption=p.replace("_", " "), use_container_width=True)


# ============================================================================
# PAGE: DETECT — IMAGE
# ============================================================================
elif page == "🖼️ Detect — Image":
    st.markdown("<div class='vid-section' style='margin-top:0;'>UPLOAD IMAGE</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        frame_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        with st.spinner("Running detection + recognition..."):
            annotated, results, elapsed_ms, detections = run_pipeline(frame_bgr)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(bgr_to_rgb(annotated), use_container_width=True, caption="Annotated output")
        with col2:
            st.markdown(
                f"<div class='vid-card'><div class='vid-metric-label'>Faces detected</div>"
                f"<div class='vid-metric-value'>{len(detections)}</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='vid-card' style='margin-top:10px;'><div class='vid-metric-label'>"
                f"Processing time</div><div class='vid-metric-value'>{elapsed_ms:.0f} ms</div></div>",
                unsafe_allow_html=True,
            )
            if results:
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(results), hide_index=True, use_container_width=True)

            success, buf = cv2.imencode(".png", annotated)
            if success:
                st.download_button(
                    "⬇ Download annotated image", data=buf.tobytes(),
                    file_name="visionid_output.png", mime="image/png", use_container_width=True,
                )
    else:
        st.info("Upload a JPG or PNG to begin. Faces will be boxed and, if recognized, labeled with an identity.")


# ============================================================================
# PAGE: DETECT — VIDEO
# ============================================================================
elif page == "🎞️ Detect — Video":
    st.markdown("<div class='vid-section' style='margin-top:0;'>UPLOAD VIDEO</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a video", type=["mp4", "avi", "mov", "mkv"], label_visibility="collapsed")
    frame_skip = st.slider("Process every Nth frame (higher = faster)", 1, 10, 2)

    if uploaded:
        in_path = f"/tmp/{uploaded.name}"
        with open(in_path, "wb") as f:
            f.write(uploaded.read())

        cap = cv2.VideoCapture(in_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        out_path = "/tmp/visionid_output.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

        progress = st.progress(0, text="Processing video...")
        preview = st.empty()
        frame_idx = 0
        last_annotated = None
        face_counts = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_skip == 0:
                annotated, results, _, detections = run_pipeline(frame)
                last_annotated = annotated
                face_counts.append(len(detections))
            else:
                annotated = last_annotated if last_annotated is not None else frame

            writer.write(annotated)
            if frame_idx % max(1, (total_frames // 20 or 1)) == 0:
                preview.image(bgr_to_rgb(annotated), caption=f"Frame {frame_idx}/{total_frames}", use_container_width=True)
            frame_idx += 1
            if total_frames:
                progress.progress(min(frame_idx / total_frames, 1.0), text=f"Processing video... {frame_idx}/{total_frames}")

        cap.release()
        writer.release()
        progress.empty()

        st.success(f"Done — processed {frame_idx} frames, avg faces/frame: {np.mean(face_counts) if face_counts else 0:.1f}")
        with open(out_path, "rb") as f:
            st.download_button("⬇ Download annotated video", f, file_name="visionid_output.mp4", mime="video/mp4")
    else:
        st.info("Upload a video file. Every Nth frame is processed for speed; intermediate frames reuse the last detection.")


# ============================================================================
# PAGE: DETECT — WEBCAM
# ============================================================================
elif page == "📸 Detect — Webcam":
    st.markdown("<div class='vid-section' style='margin-top:0;'>LIVE SNAPSHOT</div>", unsafe_allow_html=True)
    st.caption(
        "Browser-based camera capture (single frame per click — works anywhere Streamlit runs, "
        "no extra drivers needed). For continuous live video, run the included `webcam_demo.py` "
        "script locally instead."
    )
    cam_img = st.camera_input("Take a photo", label_visibility="collapsed")

    if cam_img:
        image = Image.open(cam_img).convert("RGB")
        frame_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        annotated, results, elapsed_ms, detections = run_pipeline(frame_bgr)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(bgr_to_rgb(annotated), use_container_width=True)
        with col2:
            st.markdown(
                f"<div class='vid-card'><div class='vid-metric-label'>Faces detected</div>"
                f"<div class='vid-metric-value'>{len(detections)}</div></div>",
                unsafe_allow_html=True,
            )
            if results:
                st.dataframe(pd.DataFrame(results), hide_index=True, use_container_width=True)


# ============================================================================
# PAGE: REGISTER IDENTITY
# ============================================================================
elif page == "➕ Register Identity":
    st.markdown("<div class='vid-section' style='margin-top:0;'>ENROLL A NEW IDENTITY</div>", unsafe_allow_html=True)
    st.caption("Capture 3–5 clear photos of one person's face (different angles/lighting improve accuracy).")

    name = st.text_input("Full name")
    method = st.radio("Input method", ["Upload photos", "Use webcam"], horizontal=True)

    face_imgs = []
    if method == "Upload photos":
        files = st.file_uploader("Upload face photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if files:
            for f in files:
                img = np.array(Image.open(f).convert("RGB"))
                face_imgs.append(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    else:
        cam_img = st.camera_input("Capture a photo")
        if cam_img:
            img = np.array(Image.open(cam_img).convert("RGB"))
            face_imgs.append(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            st.caption("Tip: retake with different angles and click 'Enroll' after each capture to add more samples.")

    if face_imgs:
        st.markdown("**Preview & auto-crop**")
        crops = []
        cols = st.columns(min(len(face_imgs), 5))
        for i, img in enumerate(face_imgs):
            dets = detector.detect(img)
            if not dets:
                with cols[i % 5]:
                    st.warning(f"Photo {i+1}: no face found")
                continue
            best = max(dets, key=lambda d: d["confidence"])
            crop = FaceDetector.crop_face(img, best["box"], margin=0.2)
            crops.append(crop)
            with cols[i % 5]:
                st.image(bgr_to_rgb(crop), caption=f"Photo {i+1}", use_container_width=True)

        if st.button("✅ Enroll this identity", use_container_width=True, disabled=not name or not crops):
            n = recognizer.enroll(name, crops)
            st.success(f"Enrolled '{name}' with {n} total training photo(s). Model retrained.")
            st.rerun()

    if not name:
        st.warning("Enter a name above to enable enrollment.")


# ============================================================================
# PAGE: MANAGE DATABASE
# ============================================================================
elif page == "🗂️ Manage Database":
    st.markdown("<div class='vid-section' style='margin-top:0;'>ENROLLED IDENTITIES</div>", unsafe_allow_html=True)
    people = recognizer.list_people()

    if not people:
        st.info("No identities enrolled yet. Go to *Register Identity* to add someone.")
    else:
        for p in people:
            person_dir = os.path.join(KNOWN_FACES_DIR, p)
            imgs = os.listdir(person_dir)
            with st.container():
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1:
                    if imgs:
                        st.image(cv2.cvtColor(cv2.imread(os.path.join(person_dir, imgs[0])), cv2.COLOR_BGR2RGB), width=70)
                with c2:
                    st.markdown(f"**{p.replace('_', ' ')}**  \n<span class='mono' style='color:#8A93A6;font-size:12px;'>{len(imgs)} training photo(s)</span>", unsafe_allow_html=True)
                with c3:
                    if st.button("Delete", key=f"del_{p}"):
                        recognizer.delete_person(p)
                        st.rerun()
                st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)


# ============================================================================
# PAGE: ARCHITECTURE / ABOUT
# ============================================================================
elif page == "ℹ️ Architecture":
    st.markdown(
        """
        <div class="vid-hero">
            <div class="vid-eyebrow">SYSTEM DESIGN</div>
            <div class="vid-title">How VisionID works</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
#### Pipeline

```
Input (image / video / webcam)
        │
        ▼
┌───────────────────────┐
│  1. Face Detection     │  OpenCV DNN — SSD object detector on a
│     (SSD-ResNet10)     │  ResNet-10 backbone, trained on WIDER FACE.
│     or Haar Cascade     │  Haar cascade available as a classic baseline.
└───────────────────────┘
        │  bounding boxes + confidence
        ▼
┌───────────────────────┐
│  2. Face Alignment /   │  Crop with margin, grayscale, histogram
│     Preprocessing      │  equalization, resize to 200×200.
└───────────────────────┘
        │
        ▼
┌───────────────────────┐
│  3. Face Recognition   │  LBPH (Local Binary Patterns Histogram)
│     (LBPH engine)      │  classifier trained on enrolled identities.
└───────────────────────┘
        │  identity + match confidence
        ▼
   Annotated output
```

#### Tech stack

| Layer | Choice | Why |
|---|---|---|
| Detection | OpenCV DNN (Caffe SSD, ResNet-10) | Deep-learning accuracy, CPU-only, no GPU required |
| Detection (baseline) | Haar Cascade | Classic technique, fast, included for comparison |
| Recognition | OpenCV LBPH | Lightweight, trains instantly from a few photos, no heavy native deps |
| Interface | Streamlit | Rapid, production-style web UI with zero frontend boilerplate |
| Storage | Flat-file image store + serialized model | Simple, portable, inspectable |

#### Designed to extend

The recognizer is isolated behind a single `enroll()` / `recognize()` interface
(`src/face_recognizer.py`), so swapping LBPH for a deep embedding model is a
contained change:

- **ArcFace / FaceNet** — extract a 128–512D embedding per face; store
  embeddings instead of raw images; match via cosine similarity.
- **Siamese network** — train a twin-network contrastive model to directly
  output a similarity score between two face crops, useful for one-shot
  verification (e.g., "is this the same person?") rather than closed-set
  classification.

Both are drop-in replacements because the rest of the app (detection,
UI, database management, video/webcam pipelines) only depends on the
`enroll()` / `recognize()` contract, not the underlying algorithm.

#### Known limitations

- LBPH is texture-based, not a learned embedding — it works well for a
  small enrolled population but scales worse than deep embeddings as the
  number of identities grows.
- Detection accuracy drops for extreme angles, heavy occlusion, or very
  small faces (< ~30px), inherent to the SSD-ResNet10 model.
- No liveness/anti-spoofing check — this is a recognition demo, not a
  production authentication system.
""")

st.markdown("<div class='vid-footer'>VisionID — Face Detection &amp; Recognition · Built with OpenCV + Streamlit</div>", unsafe_allow_html=True)
