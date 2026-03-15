
import cv2
import numpy as np
import torch
import os
import sys

# Optional import handling for GFPGAN
try:
    from gfpgan import GFPGANer
    GFPGAN_AVAILABLE = True
except ImportError:
    GFPGAN_AVAILABLE = False
    print("GFPGAN not found. Restoration will be limited.")

# Placeholder for CodeFormer
# Real CodeFormer usually requires cloning the repo and setting up paths
CODEFORMER_AVAILABLE = False

class Restorer:
    def __init__(self):
        self.gfpgan = None
        self.codeformer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.init_models()

    def init_models(self):
        if GFPGAN_AVAILABLE:
            try:
                # We initialize with default upscale=1, we can change it during inference or re-init
                # For efficiency, we keep one instance and handle upscaling separately if needed
                # or rely on the scaler arg if the lib supports it dynamically.
                # GFPGANer stores upscale value.
                self.gfpgan = GFPGANer(
                    model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
                    upscale=2, 
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=None # loading bg upsampler is heavier, can be done if requested
                )
            except Exception as e:
                print(f"Failed to init GFPGAN: {e}")
                self.gfpgan = None

    def restore(self, image_pil, fidelity=0.5, upscale=2, has_aligned=True, bg_enhance=True, face_upsample=True):
        """
        Restore the image using CodeFormer (if available) or GFPGAN (fallback).
        
        Args:
            image_pil: PIL Image
            fidelity: 0.0 to 1.0 (CodeFormer: 0=quality, 1=identity. GFPGAN: manual blending)
            upscale: Rescaling factor (up to 4)
            has_aligned: Pre-aligned face or not
            bg_enhance: Whether to enhance background
            face_upsample: Whether to upsample the face
        """
        img_np = np.array(image_pil)
        if img_np.ndim == 2:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
        elif img_np.shape[2] == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
            
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        output_bgr = img_bgr

        # TODO: Add actual CodeFormer inference call here if user has it installed.
        # Since we don't have it, we fallback to GFPGAN logic but map parameters.

        if self.gfpgan is not None:
            # Update scaler if needed (GFPGANer allows changing it?)
            # self.gfpgan.upscale = upscale # Hacky, might need re-init if significant
            
            # For GFPGAN, fidelity maps to "weight" of restored face vs original
            # CodeFormer: 0 (quality) -> 1 (identity). 
            # GFPGAN doesn't have a direct equivalent 'fidelity' slider in usage normally, 
            # usually it just restores. We can blend result with original.
            
            # Using GFPGAN
            try:
                # cropped_faces, restored_faces, restored_img
                _, _, restored_img = self.gfpgan.enhance(
                    img_bgr, 
                    has_aligned=has_aligned, 
                    only_center_face=False, 
                    paste_back=True,
                    weight=0.5 # Default GFPGAN weight
                )
                
                # Apply blending for "fidelity" simulation if using GFPGAN
                # If codeformer fidelity is high (better identity), we might blend more of original?
                # Actually CodeFormer's fidelity is: 0.0 (high restoration) ... 1.0 (keep original details/identity)
                # So we blend: output = restored * (1-fidelity) + original * fidelity
                
                # Resize original to match restored if upscale > 1 happened
                if restored_img.shape[:2] != img_bgr.shape[:2]:
                    h, w = restored_img.shape[:2]
                    img_bgr_resized = cv2.resize(img_bgr, (w, h), interpolation=cv2.INTER_LINEAR)
                    output_bgr = cv2.addWeighted(restored_img, 1.0 - fidelity, img_bgr_resized, fidelity, 0)
                else:
                    output_bgr = cv2.addWeighted(restored_img, 1.0 - fidelity, img_bgr, fidelity, 0)
                
                # Handle upscale resizing if GFPGAN didn't do it to target or if we want specific scale
                # GFPGANer(upscale=2) was set.
                
            except Exception as e:
                print(f"GFPGAN process failed: {e}")
                output_bgr = img_bgr 
        else:
            # Basic sharpening fallback
            kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
            output_bgr = cv2.filter2D(img_bgr, -1, kernel)
            
            # Handle upscale manual
            if upscale > 1:
                h, w = output_bgr.shape[:2]
                output_bgr = cv2.resize(output_bgr, (w * upscale, h * upscale), interpolation=cv2.INTER_CUBIC)

        return cv2.cvtColor(output_bgr, cv2.COLOR_BGR2RGB)
