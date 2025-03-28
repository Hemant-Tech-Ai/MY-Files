import os
import fitz
import pdfplumber
import pandas as pd
import tempfile
import zipfile
from pathlib import Path
from PIL import Image
import pytesseract
from transformers import AutoTokenizer, AutoModel
import torch
import torchvision.transforms as T
from torchvision.transforms.functional import InterpolationMode

class DocumentProcessor:
    def __init__(self, device="cpu", input_size=448):
        # Set Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.device = torch.device(device)
        self.input_size = input_size
        self.dtype = torch.float32
        
        # Initialize handwritten model
        try:
            self.model, self.tokenizer = self._load_handwritten_model()
            self.generation_config = {
                "max_new_tokens": 128,
                "pad_token_id": self.tokenizer.eos_token_id
            }
            self.system_instruction = (
                "Extract only the visible text from the image as it appears. "
                "Do not add, summarize, or paraphrase. "
                "Exclude repeated lines, symbols, and irrelevant content."
            )
        except Exception as e:
            print(f"Warning: Handwritten model not loaded: {str(e)}")
            self.model = None
            self.tokenizer = None

    def _load_handwritten_model(self):
        try:
            local_path = Path("models/InternVL2_5-1B")
            model_path = str(local_path.absolute()) if local_path.exists() else "OpenGVLab/InternVL2_5-1B"
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                use_fast=False
            )
            
            model = AutoModel.from_pretrained(
                model_path,
                torch_dtype=self.dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            ).to(self.device)
            
            model.eval()
            return model, tokenizer
        except Exception as e:
            raise RuntimeError(f"Model loading error: {str(e)}")

    def process_image(self, image_path):
        """Process printed text from image"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"Error processing image: {str(e)}")

    def process_handwritten(self, image_path):
        """Process handwritten text from image"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Handwritten model not initialized")
            
        try:
            # Preprocess image
            image = Image.open(image_path)
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            transform = T.Compose([
                T.Resize((self.input_size, self.input_size), interpolation=InterpolationMode.BICUBIC),
                T.ToTensor(),
                T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
            ])
            
            pixel_values = transform(image).unsqueeze(0).to(self.device, dtype=self.dtype)
            
            # Process with model
            prompt = f"<image>\n{self.system_instruction}\n\n"
            response = self.model.chat(
                tokenizer=self.tokenizer,
                pixel_values=pixel_values,
                question=prompt,
                generation_config=self.generation_config,
                history=None,
                return_history=False
            )
            
            return " ".join(response.splitlines())
        except Exception as e:
            raise RuntimeError(f"Handwritten processing failed: {str(e)}")

    def process_pdf(self, pdf_path):
        """Process PDF document"""
        try:
            temp_dir = tempfile.mkdtemp()
            images_dir = os.path.join(temp_dir, "images")
            tables_dir = os.path.join(temp_dir, "tables")
            texts_dir = os.path.join(temp_dir, "texts")
            
            for dir_path in [images_dir, tables_dir, texts_dir]:
                os.makedirs(dir_path, exist_ok=True)

            # Extract content
            extracted_images = self._extract_images(pdf_path, images_dir)
            extracted_tables = self._extract_tables(pdf_path, tables_dir)
            extracted_texts = self._extract_text(pdf_path, texts_dir)

            # Create zip file
            zip_path = os.path.join(temp_dir, "extracted_content.zip")
            self._create_zip(zip_path, [images_dir, tables_dir, texts_dir])

            return {
                'images': extracted_images,
                'tables': extracted_tables,
                'texts': extracted_texts,
                'zip_path': zip_path
            }
        except Exception as e:
            raise RuntimeError(f"Error processing PDF: {str(e)}")

    def _extract_images(self, pdf_path, output_dir):
        """Extract images from PDF"""
        extracted_images = []
        pdf_document = fitz.open(pdf_path)

        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            images = page.get_images(full=True)

            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                image_path = os.path.join(
                    output_dir,
                    f"page_{page_number + 1}_image_{img_index + 1}.png"
                )
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                extracted_images.append(image_path)

        pdf_document.close()
        return extracted_images

    def _extract_tables(self, pdf_path, output_dir):
        """Extract tables from PDF"""
        extracted_tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                # Debug table detection
                debug_image = page.to_image()
                debug_image.draw_rects(page.debug_tablefinder().edges)
                debug_image_path = os.path.join(output_dir, f"page_{i}_tables_debug.png")
                debug_image.save(debug_image_path)

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for j, table in enumerate(tables, start=1):
                        df = pd.DataFrame(table[1:], columns=table[0])
                        output_csv = os.path.join(output_dir, f"page_{i}_table_{j}.csv")
                        df.to_csv(output_csv, index=False)
                        extracted_tables.append(output_csv)

        return extracted_tables

    def _extract_text(self, pdf_path, output_dir):
        """Extract text with positioning from PDF"""
        extracted_texts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                # Get table regions to exclude
                tables = page.find_tables()
                table_bboxes = [table.bbox for table in tables]

                # Extract characters excluding table regions
                characters = page.chars
                non_table_chars = [
                    char for char in characters
                    if not any(
                        bbox[0] <= float(char["x0"]) <= bbox[2]
                        and bbox[1] <= float(char["top"]) <= bbox[3]
                        for bbox in table_bboxes
                    )
                ]

                # Sort and reconstruct text
                non_table_chars.sort(key=lambda c: (float(c["top"]), float(c["x0"])))
                reconstructed_text = self._reconstruct_text(non_table_chars)

                # Save text
                text_file_path = os.path.join(output_dir, f"page_{page_number + 1}.txt")
                with open(text_file_path, "w", encoding="utf-8") as text_file:
                    text_file.write(reconstructed_text)
                extracted_texts.append(text_file_path)

        return extracted_texts

    def _reconstruct_text(self, chars, new_line_threshold=5, space_gap_threshold=1):
        """Reconstruct text from characters with proper spacing"""
        reconstructed_text = ""
        last_top = None
        last_x1 = None
        line_buffer = []

        for char in chars:
            current_top = float(char["top"])
            current_x0 = float(char["x0"])
            current_x1 = float(char["x1"])
            text_char = char["text"]

            if last_top is None or abs(current_top - last_top) > new_line_threshold:
                if line_buffer:
                    reconstructed_text += "".join(line_buffer) + "\n"
                line_buffer = [text_char]
                last_top = current_top
                last_x1 = current_x1
            else:
                if last_x1 is not None:
                    gap = current_x0 - last_x1
                    if gap > space_gap_threshold and text_char not in [" ", "\t"]:
                        if not line_buffer or line_buffer[-1] != " ":
                            line_buffer.append(" ")

                line_buffer.append(text_char)
                last_x1 = current_x1
                last_top = current_top

        if line_buffer:
            reconstructed_text += "".join(line_buffer) + "\n"

        return reconstructed_text

    def _create_zip(self, zip_path, directories):
        """Create ZIP file containing all extracted content"""
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for directory in directories:
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(directory))
                        zipf.write(file_path, arcname)