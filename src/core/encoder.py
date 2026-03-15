
import torch
import clip
from PIL import Image
import os
import sys

# Add src to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class CLIPEncoder:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.preprocess = None
        self.load_model()

    def load_model(self):
        # Determine model path
        model_path = None
        if os.path.exists(config.FINE_TUNED_MODEL_PATH_SYSTEM):
            model_path = config.FINE_TUNED_MODEL_PATH_SYSTEM
            print(f"Loading fine-tuned model from SYSTEM path: {model_path}")
        elif os.path.exists(config.FINE_TUNED_MODEL_PATH_LOCAL):
            model_path = config.FINE_TUNED_MODEL_PATH_LOCAL
            print(f"Loading fine-tuned model from LOCAL path: {model_path}")
        else:
            print("Fine-tuned model NOT found. Falling back to base CLIP.")

        # Load Base CLIP
        print(f"Loading base CLIP {config.CLIP_MODEL_NAME}...")
        self.model, self.preprocess = clip.load(config.CLIP_MODEL_NAME, device=self.device)

        # Load Fine-tuned weights if available
        if model_path:
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                # Handle different state_dict keys if necessary (often DataParallel or saved differently)
                state_dict = checkpoint['state_dict'] if 'state_dict' in checkpoint else checkpoint
                
                # Check for prefix 'module.' which happens when trained with DataParallel
                new_state_dict = {}
                for k, v in state_dict.items():
                    name = k[7:] if k.startswith('module.') else k 
                    new_state_dict[name] = v
                
                # In strict=False mode to allow for potential head mismatches if only backbone is needed
                # But requirement says "Only the CLIP encoder is used for embeddings", so we load what fits.
                missing, unexpected = self.model.load_state_dict(new_state_dict, strict=False)
                print(f"Fine-tuned weights loaded. Missing: {len(missing)}, Unexpected: {len(unexpected)}")
            except Exception as e:
                print(f"Error loading fine-tuned weights: {e}. using base CLIP.")

        self.model.eval()

    def encode_image(self, image):
        """
        Encodes a PIL Image or list of PIL Images.
        """
        if isinstance(image, list):
            images = [self.preprocess(img).unsqueeze(0).to(self.device) for img in image]
            batch = torch.cat(images)
        else:
            batch = self.preprocess(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model.encode_image(batch)
            features = features / features.norm(dim=-1, keepdim=True)
            
        return features.cpu().numpy()

    def encode_text(self, text):
        """
        Encodes a text string.
        """
        text_token = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            features = self.model.encode_text(text_token)
            features = features / features.norm(dim=-1, keepdim=True)
        
        return features.cpu().numpy()
