import time
from pathlib import Path
import os
import torch
import fitz
import pdfplumber
import pandas as pd
import tempfile
import zipfile
from PIL import Image
import torchvision.transforms as T
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoTokenizer, AutoModel
from onnxtr.io import DocumentFile
from onnxtr.models import ocr_predictor, EngineConfig
import streamlit as st

class ModelManager:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
    def create_typed_model(self):
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
    def __init__(self, input_size=448):
        self.input_size = input_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
    def preprocess_image(self, image_path):
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        transform = T.Compose([
            T.Resize((self.input_size, self.input_size), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
        ])
        
        return transform(image).unsqueeze(0).to(self.device, dtype=self.dtype)

class PDFProcessor:
    def __init__(self):
        self.temp_dir = None
        self.images_dir = None
        self.tables_dir = None
        self.texts_dir = None
        
    def setup_directories(self):
        self.temp_dir = tempfile.mkdtemp()
        self.images_dir = os.path.join(self.temp_dir, "images")
        self.tables_dir = os.path.join(self.temp_dir, "tables")
        self.texts_dir = os.path.join(self.temp_dir, "texts")
        
        for dir_path in [self.images_dir, self.tables_dir, self.texts_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def extract_images(self, pdf_document):
        extracted_images = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            images = page.get_images(full=True)
            
            for img_idx, img in enumerate(images):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                
                image_path = os.path.join(self.images_dir, f"page_{page_num + 1}_image_{img_idx + 1}.png")
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                extracted_images.append(image_path)
        return extracted_images
    
    def extract_tables_and_text(self, pdf):
        extracted_tables = []
        extracted_texts = []
        
        for page_num, page in enumerate(pdf.pages):
            # Extract tables
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    table_path = os.path.join(self.tables_dir, f"page_{page_num + 1}_table_{table_idx + 1}.csv")
                    df.to_csv(table_path, index=False)
                    extracted_tables.append(table_path)
            
            # Extract text
            text = page.extract_text()
            if text.strip():
                text_path = os.path.join(self.texts_dir, f"page_{page_num + 1}.txt")
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(text)
                extracted_texts.append(text_path)
                
        return extracted_tables, extracted_texts
    
    def create_zip(self):
        zip_path = os.path.join(self.temp_dir, "extracted_content.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for folder in [self.images_dir, self.tables_dir, self.texts_dir]:
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.temp_dir)
                        zipf.write(file_path, arcname)
        return zip_path

class DocuMindO:
    def __init__(self):
        self.model_manager = ModelManager()
        self.image_processor = ImageProcessor()
        self.pdf_processor = PDFProcessor()
        
        # Initialize models
        if not hasattr(DocuMindO, '_typed_model'):
            DocuMindO._typed_model = self.model_manager.create_typed_model()
        if not hasattr(DocuMindO, '_handwritten_model') or not hasattr(DocuMindO, '_tokenizer'):
            DocuMindO._handwritten_model, DocuMindO._tokenizer = self.model_manager.create_handwritten_model()

    def process_image(self, image_path, doc_type='typed', user_prompt=None):
        try:
            if doc_type.lower() == 'typed':
                return self._process_typed_image(image_path)
            else:
                return self._process_handwritten_image(image_path, user_prompt)
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    # def _process_typed_image(self, image_path):
    #     single_img_doc = DocumentFile.from_images(str(image_path))
    #     result = DocuMindO._typed_model(single_img_doc)
    #     extracted_text = result.render()
    #     return self._create_response(extracted_text)

    def _process_handwritten_image(self, image_path, user_prompt):
        pixel_values = self.image_processor.preprocess_image(image_path)
        default_prompt = ("Extract only visible text from the image as written. "
                         "Do not summarize, paraphrase, or add any extra words. "
                         "Ignore repeated lines, special symbols, and irrelevant content. "
                         "Include each unique name, address, or detail only once.")
        
        response = DocuMindO._handwritten_model.chat(
            tokenizer=DocuMindO._tokenizer,
            pixel_values=pixel_values,
            question=user_prompt or default_prompt,
            generation_config=dict(
                max_new_tokens=128,
                pad_token_id=DocuMindO._tokenizer.eos_token_id
            ),
            history=None,
            return_history=False
        )
        return self._create_response(response)

    def _create_response(self, text):
        return {
            'status': 'success',
            'original_text': text,
            'modified_text': text,
            'message': 'Text extracted successfully'
        }

    # def process_pdf(self, pdf_path):
    #     try:
    #         self.pdf_processor.setup_directories()
            
    #         # Extract images using PyMuPDF
    #         pdf_document = fitz.open(pdf_path)
    #         extracted_images = self.pdf_processor.extract_images(pdf_document)
            
    #         # Extract tables and text using pdfplumber
    #         with pdfplumber.open(pdf_path) as pdf:
    #             extracted_tables, extracted_texts = self.pdf_processor.extract_tables_and_text(pdf)
            
    #         # Create zip file
    #         zip_path = self.pdf_processor.create_zip()
            
    #         return {
    #             'images': extracted_images,
    #             'tables': extracted_tables,
    #             'texts': extracted_texts,
    #             'zip_path': zip_path
    #         }

    #     except Exception as e:
    #         raise Exception(f"Error processing PDF: {str(e)}")

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