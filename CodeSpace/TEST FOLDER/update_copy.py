import time
from pathlib import Path
import os
import torch
import fitz
import pandas as pd
import tempfile
import zipfile
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
from PIL import Image
import torchvision.transforms as T
from torchvision.transforms.functional import InterpolationMode
from onnxtr.io import DocumentFile
from  onnxtr.models import ocr_predictor, EngineConfig
import streamlit as st

class DocuMindO:
    _typed_model = None
    _handwritten_model = None
    _tokenizer = None

    def __init__(self):
        if DocuMindO._typed_model is None:
            DocuMindO._typed_model = self._create_model('crnn_mobilenet_v3_large')
        if DocuMindO._handwritten_model is None or DocuMindO._tokenizer is None:
            DocuMindO._handwritten_model, DocuMindO._tokenizer = self._create_handwritten_model()

    def _create_model(self, reco_arch):
        return ocr_predictor(
            det_arch='fast_base',
            reco_arch=reco_arch,
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
    
    def _create_handwritten_model(self):
        MODEL_PATH_HANDWRITTEN = "OpenGVLab/InternVL2_5-1B"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH_HANDWRITTEN, trust_remote_code=True, use_fast=False)
        tokenizer.pad_token = tokenizer.eos_token

        model_handwritten = AutoModel.from_pretrained(
            MODEL_PATH_HANDWRITTEN,
            torch_dtype=dtype,  
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).to(device).eval()
        return model_handwritten, tokenizer

    def process_image(self, image_path, doc_type='typed', user_prompt=None):
        try:
            if doc_type.lower() == 'typed':
                single_img_doc = DocumentFile.from_images(str(image_path))
                result = DocuMindO._typed_model(single_img_doc)
                extracted_text = result.render()
            else:
                pixel_values = self.preprocess_image(image_path)
                response = DocuMindO._handwritten_model.chat(
                    tokenizer=DocuMindO._tokenizer,
                    pixel_values=pixel_values,
                    question=user_prompt or "Extract only visible text from the image as written. Do not summarize, paraphrase, or add any extra words. Ignore repeated lines, special symbols, and irrelevant content. Include each unique name, address, or detail only once.",
                    generation_config=dict(max_new_tokens=128, pad_token_id=DocuMindO._tokenizer.eos_token_id),
                    history=None,
                    return_history=False
                )
                extracted_text = response

            # Return the extracted text without displaying it
            return {
                'status': 'success',
                'original_text': extracted_text,
                'modified_text': extracted_text,
                'message': 'Text extracted successfully'
            }

        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def get_user_input(self, extracted_text):
        """Method to get user input for text correction or questions"""
        # Use Streamlit's text input for user corrections or questions
        user_correction = st.text_area("Enter your corrections or questions (leave blank to skip):", "")
        
        if user_correction.strip():
            return {
                'status': 'success',
                'original_text': extracted_text,
                'modified_text': user_correction,
                'message': 'User input received'
            }
        else:
            return {
                'status': 'success',
                'original_text': extracted_text,
                'modified_text': extracted_text,
                'message': 'No modifications made'
            }

    def preprocess_image(self, image_path, input_size=448):
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        transform = T.Compose([
            T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
        ])
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        return transform(image).unsqueeze(0).to(device, dtype=dtype)
