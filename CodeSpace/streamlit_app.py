import streamlit as st
import os
import fitz
import cv2
from unstructured.partition.image import partition_image
import numpy as np
import tensorflow as tf
from paddleocr import PaddleOCR
import pandas as pd
import tempfile
import logging
import warnings
from pathlib import Path

# Suppress warnings and logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger("ppocr").setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

class PDFProcessor:
    def __init__(self):
        self.ocr = PaddleOCR(lang='en')

    def process_pdf(self, pdf_file, progress_bar=None):
        """Process PDF and extract content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create output directories
            output_dirs = {
                'text': os.path.join(temp_dir, "Extracted Text"),
                'tables': os.path.join(temp_dir, "Extracted Tables"),
                'tables_csv': os.path.join(temp_dir, "Extracted Tables CSV"),
                'images': os.path.join(temp_dir, "Extracted Images")
            }
            
            for dir_path in output_dirs.values():
                os.makedirs(dir_path, exist_ok=True)

            # Process PDF
            pdf_document = fitz.open(pdf_file)
            total_pages = pdf_document.page_count
            
            results = {
                'texts': [],
                'tables': [],
                'images': [],
                'csvs': []
            }

            for page_number in range(total_pages):
                if progress_bar:
                    progress_bar.progress((page_number + 1) / total_pages)
                
                page = pdf_document[page_number]
                page_name = f'page_{page_number + 1}'
                
                # Process page
                self._process_page(page, page_name, output_dirs, results)

            pdf_document.close()
            return results

    def _process_page(self, page, page_name, output_dirs, results):
        """Process a single PDF page"""
        # Convert page to image
        pix = page.get_pixmap(dpi=300, colorspace=fitz.csRGB)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        image_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # Save temporary image for processing
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, image_cv)
            
            # Extract elements
            elements = partition_image(filename=tmp_file.name, infer_table_structure=True, strategy='hi_res')
            
            # Process elements
            for element in elements:
                element_dict = element.to_dict()
                if element_dict.get("type") == "Table":
                    self._process_table(element_dict, image_cv, page_name, output_dirs, results)
                else:
                    self._process_text(element_dict, page_name, output_dirs, results)

            os.unlink(tmp_file.name)

    def _process_table(self, element_dict, image_cv, page_name, output_dirs, results):
        """Process and save table"""
        try:
            coordinates = element_dict["metadata"]["coordinates"]["points"]
            
            # Crop table
            x_min = int(min(pt[0] for pt in coordinates))
            y_min = int(min(pt[1] for pt in coordinates))
            x_max = int(max(pt[0] for pt in coordinates))
            y_max = int(max(pt[1] for pt in coordinates))
            
            cropped_table = image_cv[y_min:y_max, x_min:x_max]
            
            # Save table image
            table_filename = f"{page_name}_Table_{len(results['tables']) + 1}.png"
            table_path = os.path.join(output_dirs['tables'], table_filename)
            cv2.imwrite(table_path, cropped_table)
            results['tables'].append(table_path)
            
            # Process table with OCR and save CSV
            self._save_table_csv(cropped_table, page_name, output_dirs, results)
            
        except Exception as e:
            st.error(f"Error processing table: {str(e)}")

    def _save_table_csv(self, table_image, page_name, output_dirs, results):
        """Convert table image to CSV"""
        output = self.ocr.ocr(table_image)[0]
        if not output:
            return

        # Extract text and positions
        boxes = [line[0] for line in output]
        texts = [line[1][0] for line in output]
        
        # Create DataFrame and save CSV
        df = pd.DataFrame({'text': texts})
        csv_filename = f"{page_name}_Table_{len(results['csvs']) + 1}.csv"
        csv_path = os.path.join(output_dirs['tables_csv'], csv_filename)
        df.to_csv(csv_path, index=False)
        results['csvs'].append(csv_path)

    def _process_text(self, element_dict, page_name, output_dirs, results):
        """Process and save text"""
        text_content = element_dict.get("text", "")
        if text_content:
            text_filename = f"{page_name}_text.txt"
            text_path = os.path.join(output_dirs['text'], text_filename)
            with open(text_path, "a", encoding="utf-8") as text_file:
                text_file.write(text_content + "\n")
            results['texts'].append(text_path)

def main():
    st.set_page_config(page_title="PDF Processor", layout="wide")
    st.title("PDF Processing App")

    processor = PDFProcessor()
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
    
    if uploaded_file:
        if st.button("Process PDF"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    
                    status_text.text("Processing PDF...")
                    results = processor.process_pdf(tmp_file.name, progress_bar)
                    
                    # Display results in tabs
                    tabs = st.tabs(["Tables", "Text", "CSVs"])
                    
                    with tabs[0]:
                        st.subheader("Extracted Tables")
                        for table_path in results['tables']:
                            st.image(table_path)
                            
                    with tabs[1]:
                        st.subheader("Extracted Text")
                        for text_path in results['texts']:
                            with open(text_path, 'r', encoding='utf-8') as f:
                                st.text_area("", f.read(), height=200)
                    
                    with tabs[2]:
                        st.subheader("Table CSVs")
                        for csv_path in results['csvs']:
                            df = pd.read_csv(csv_path)
                            st.dataframe(df)
                    
                    status_text.text("Processing complete!")
                    
                os.unlink(tmp_file.name)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                
            finally:
                progress_bar.empty()

if __name__ == "__main__":
    main() 