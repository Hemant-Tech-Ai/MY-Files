import os
import torch
import streamlit as st
from pathlib import Path
import tempfile  # Keep this as it's used for image processing
from PIL import Image

# Separate try-except for model imports
try:
    from transformers import AutoTokenizer, AutoModel
    import torchvision.transforms as T
    from torchvision.transforms.functional import InterpolationMode
    from onnxtr.io import DocumentFile
    from onnxtr.models import ocr_predictor, EngineConfig
except ImportError as e:
    st.error(f"Failed to import required modules: {str(e)}")
    raise

class ModelManager:
    """Manages model creation and initialization"""
    def __init__(self):
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        except Exception as e:
            st.error(f"Error initializing ModelManager: {str(e)}")
            raise

    def create_typed_model(self):
        """Create OCR model for typed text"""
        return ocr_predictor(
            det_arch='fast_base',
            reco_arch='crnn_mobilenet_v3_large',
            det_bs=1,
            reco_bs=64,
            assume_straight_pages=True,
            straighten_pages=True,
            export_as_straight_boxes=True,
            preserve_aspect_ratio=True,
            symmetric_pad=True,
            detect_orientation=True,
            detect_language=True,
            disable_crop_orientation=True,
            disable_page_orientation=True,
            resolve_lines=True,
            resolve_blocks=True,
            paragraph_break=0.035,
            load_in_8_bit=False,
            det_engine_cfg=EngineConfig(),
            reco_engine_cfg=EngineConfig(),
            clf_engine_cfg=EngineConfig(),
        )

    def create_handwritten_model(self):
        """Create model for handwritten text"""
        MODEL_PATH = "OpenGVLab/InternVL2_5-1B"
        
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH, 
            trust_remote_code=True, 
            use_fast=False
        )
        tokenizer.pad_token = tokenizer.eos_token

        model = AutoModel.from_pretrained(
            MODEL_PATH,
            torch_dtype=self.dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).to(self.device).eval()
        
        return model, tokenizer

class ImageProcessor:
    """Handles image preprocessing and processing"""
    def __init__(self, device="cpu", input_size=448):
        self.device = device
        self.input_size = input_size
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        transform = T.Compose([
            T.Resize((self.input_size, self.input_size), 
                    interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=(0.485, 0.456, 0.406), 
                       std=(0.229, 0.224, 0.225))
        ])
        
        return transform(image).unsqueeze(0).to(self.device, dtype=self.dtype)

    def process_typed_text(self, image_path, model):
        """Process typed text from image"""
        single_img_doc = DocumentFile.from_images(str(image_path))
        result = model(single_img_doc)
        return result.render()

    def clean_extracted_text(self, text):
        """Clean and remove duplicate lines from extracted text"""
        if not text:
            return text
            
        # Split text into lines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Remove duplicate lines while preserving order
        seen = set()
        cleaned_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                cleaned_lines.append(line)
        
        # Join lines back together
        return '\n'.join(cleaned_lines)

    def process_handwritten_text(self, image_path, model, tokenizer, user_prompt=None):
        """Process handwritten text from image"""
        pixel_values = self.preprocess_image(image_path)
        
        # Base system prompt
        default_prompt = (
            "Extract only visible text from the image as written. "
            "Do not summarize, paraphrase, or add any extra words. "
            "Ignore repeated lines, special symbols, and irrelevant content. "
            "Include each unique name, address, or detail only once."
        )
        
        # Combine prompts if user provided additional instructions
        if user_prompt and user_prompt.strip():
            final_prompt = (
                f"{default_prompt}\n\n"
                f"Additional Instructions: {user_prompt.strip()}\n"
                "Follow both the base rules and additional instructions while extracting text."
            )
        else:
            final_prompt = default_prompt
            
        # Add image tag and format prompt
        prompt = f"<image>\n{final_prompt}\n\n"
        
        response = model.chat(
            tokenizer=tokenizer,
            pixel_values=pixel_values,
            question=prompt,
            generation_config=dict(
                max_new_tokens=128,
                pad_token_id=tokenizer.eos_token_id
            ),
            history=None,
            return_history=False
        )
        
        # Clean and remove duplicates from the response
        cleaned_text = self.clean_extracted_text(response)
        return cleaned_text

    def save_temp_image(self, image_data):
        """Save uploaded image data to temporary file"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_data)
                return tmp_file.name
        except Exception as e:
            raise Exception(f"Error saving temporary image: {str(e)}")

class DocuMindO:
    """Main document processing class"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DocuMindO, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not DocuMindO._initialized:
            try:
                self.model_manager = ModelManager()
                self.image_processor = ImageProcessor(
                    device="cuda" if torch.cuda.is_available() else "cpu"
                )
                
                # Initialize models
                self._initialize_models()
                
                DocuMindO._initialized = True
            except Exception as e:
                st.error(f"Error initializing DocuMindO: {str(e)}")
                raise

    def _initialize_models(self):
        """Initialize models with proper error handling"""
        try:
            if not hasattr(self, '_typed_model'):
                self._typed_model = self.model_manager.create_typed_model()
            
            if not hasattr(self, '_handwritten_model') or not hasattr(self, '_tokenizer'):
                self._handwritten_model, self._tokenizer = self.model_manager.create_handwritten_model()
        except Exception as e:
            st.error(f"Error initializing models: {str(e)}")
            raise

    def process_image(self, image_path, doc_type='typed', user_prompt=None):
        """Process image based on document type"""
        try:
            if not os.path.exists(image_path):
                raise Exception(f"Image file not found: {image_path}")

            if doc_type.lower() == 'handwritten':
                extracted_text = self.image_processor.process_handwritten_text(
                    image_path,
                    self._handwritten_model,
                    self._tokenizer,
                    user_prompt
                )
            else:
                extracted_text = self.image_processor.process_typed_text(
                    image_path, 
                    self._typed_model
                )
                # Clean typed text as well
                extracted_text = self.image_processor.clean_extracted_text(extracted_text)

            return {
                'status': 'success',
                'original_text': extracted_text,
                'modified_text': extracted_text,
                'message': 'Text extracted successfully'
            }

        except Exception as e:
            return {
                'status': 'error',
                'original_text': '',
                'modified_text': '',
                'message': f"Error processing image: {str(e)}"
            }

    def get_user_input(self, extracted_text):
        """Get user input for text correction"""
        user_correction = st.text_area(
            "Enter your corrections or questions (leave blank to skip):",
            ""
        )
        
        if user_correction.strip():
            return {
                'status': 'success',
                'original_text': extracted_text,
                'modified_text': user_correction,
                'message': 'User input received'
            }
        return {
            'status': 'success',
            'original_text': extracted_text,
            'modified_text': extracted_text,
            'message': 'No modifications made'
        } 
    
