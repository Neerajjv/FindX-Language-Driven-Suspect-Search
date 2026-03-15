
import os

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CCTV_FOLDER = r"D:\clg\FindX\CCTV"  # Fixed CCTV folder as per requirements
MODELS_DIR_SYSTEM = r"C:\FindX\models"
MODELS_DIR_LOCAL = os.path.join(BASE_DIR, "model")

# File Paths
CCTV_INDEX_PATH = os.path.join(BASE_DIR, "cctv_index.faiss")
CCTV_META_PATH = os.path.join(BASE_DIR, "cctv_meta.json")

# Model Paths
# Priority: System Path -> Local Path
FINE_TUNED_MODEL_NAME = "best_token_attr_clip.pth"
FINE_TUNED_MODEL_PATH_SYSTEM = os.path.join(MODELS_DIR_SYSTEM, FINE_TUNED_MODEL_NAME)
FINE_TUNED_MODEL_PATH_LOCAL = os.path.join(MODELS_DIR_LOCAL, "best_attr_head_clip.pth") # User mentioned this specific name in request

# Settings
FRAME_SAMPLE_RATE = 5  # FPS for extraction
CLIP_MODEL_NAME = "ViT-B/16"
DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") != "-1" else "cpu" # Basic check, will refine in code

# UI Constants
THUMBNAIL_SIZE = (150, 150)
