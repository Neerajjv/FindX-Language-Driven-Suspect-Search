<div align="center">

# 🔍 FindX

**Text-Based Person Identification in CCTV | AI-Powered Search & Restoration**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-ee4c2c.svg)](https://pytorch.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-yellow.svg)](https://github.com/ultralytics/ultralytics)
[![OpenAI CLIP](https://img.shields.io/badge/OpenAI-CLIP-black.svg)](https://github.com/openai/CLIP)
[![FAISS](https://img.shields.io/badge/Meta-FAISS-blue.svg)](https://github.com/facebookresearch/faiss)

</div>

<br>

## Problem Statement
Reviewing hours of CCTV footage to locate a specific individual is a labor-intensive and error-prone process. Security personnel often need to find a suspect or missing person based on a description of their clothing or accessories (e.g., *"person wearing a red hoodie and black backpack"*). Manually scanning video files for these visual cues is inefficient and can lead to missed critical evidence.

## Proposed Idea & Solution
**FindX** is an AI-powered desktop application designed to streamline the process of person identification in CCTV footage. It leverages state-of-the-art deep learning models to index video content, allowing users to search for people using natural language queries.

The system automatically:
1.  **Detects** people in video frames using YOLOv8.
2.  **Extracts** high-quality crops of individuals at optimal FPS.
3.  **Encodes** visual features into searchable vectors using OpenAI's CLIP model.
4.  **Indexes** these vectors using FAISS for millisecond-level retrieval.

Users can simply type a description like *"man in blue shirt"* to see all matching occurrences, instantly playback the video at the relevant timestamp, and even enhance low-quality face images for better identification natively within the app.

---

## Tech Stack & Architecture

The project is built using a robust, modern Python stack:

### **Backend Core (`src/core`)**
-   **Deep Learning Engine**: PyTorch, Torchvision
-   **Object Detection (`detector.py`)**: YOLOv8 (via `ultralytics`)
-   **Feature Extraction (`encoder.py`)**: OpenAI CLIP (`ViT-B/16`) for joint text-image embeddings
-   **Vector Search (`indexer.py`)**: FAISS (Facebook AI Similarity Search)
-   **Video Processing (`processor.py`)**: OpenCV for efficient frame extraction
-   **Image Restoration (`restoration.py`)**: GFPGAN for face enhancement and upscaling
-   **Image Processing**: Pillow, NumPy

### **Frontend GUI (`src/ui`)**
-   **Framework**: PyQt6
-   **Components**: Custom dark theme styling, Interactive panels (`viewer.py`, `sidebar.py`, `results_grid.py`, `restoration_panel.py`)

---

## Key Features

### 1. Natural Language Search
Search for specific people using descriptive text queries. The CLIP model understands rich semantic attributes like color *(red shirt)*, object *(backpack)*, and type *(woman/man/child)*.

### 2. Automated CCTV Indexing
Point the application to your CCTV storage folder, and it will automatically scan, detect, and index all person occurrences in the background at an optimized frame sample rate (e.g., 5 FPS).

### 3. Smart Video Playback
Clicking on any search result instantly opens the built-in video player, jumping exactly to the timestamp where the person was detected, with the individual highlighted.

### 4. Interactive Results Grid
View search results in a clean, scrollable grid of cropped images, ranked dynamically by relevance to your text query.

### 5. Integrated Image Restoration
CCTV footage is often blurry or pixelated. FindX includes an integrated restoration tool powered by GFPGAN to upscale and clear up low-resolution face crops natively, aiding rapid identification.

### 6. Single Video Upload
Apart from batch processing CCTV folders, you can upload and analyze single video files for quick investigations.

---

## Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/FindX.git
    cd FindX
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    
    # On Windows:
    venv\Scripts\activate
    # On Linux/macOS:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    > **Note:** Ensure you have PyTorch installed with **CUDA support** if you have a compatible NVIDIA GPU. This significantly accelerates YOLOv8 detection and CLIP embedding processes.

4.  **Model Setup**
    - The code pulls models locally from `model/` or dynamically loads them. Make sure the `.pt` and `.pth` weights (like `yolov8n.pt`, `yolov8n-pose.pt`) are downloaded/ready.

5.  **Run the Application**
    ```bash
    python app.py
    ```

---

## Usage Workflow
1.  **Launch** the app by running `app.py`.
2.  **Select Mode**: Choose **"CCTV"** to scan a directory or **"Upload"** for a single file from the sidebar.
3.  **Indexing**: Click **"Scan"** to process videos. (The first run may take time depending on video length and GPU availability).
4.  **Search**: Enter a description (e.g., *"white t-shirt"*) in the top search bar and hit Enter.
5.  **Review**: Click on result cards to view the video loop or use the **Restoration panel** to enhance details.

---

## Project Structure
```text
FindX/
├── app.py                  # Main entry point for the PyQt6 application
├── cctv_index.faiss        # FAISS index for quick vector search caching
├── requirements.txt        # Python dependencies
├── src/                    # Source Code
│   ├── config.py           # Application configurations and constants
│   ├── core/               # Backend modules (Detector, Encoder, Indexer, etc.)
│   └── ui/                 # Frontend PyQt6 widgets (MainWindow, Panels, Views)
├── model/                  # Local directory for stored PyTorch weights
├── data/                   # Data directory for outputs / temp files
└── README.md               # Project documentation
```

---
## 👥 Meet the Team

*   **Neeraj J V**
*   **Padmesh J**
*   **Raj Mohan R**

*Built for robust and efficient text-based intelligence gathering.*
