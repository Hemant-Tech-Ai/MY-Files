
### csv DATA Frame is used to display the table in the UI

import os
import fitz
import pandas as pd
import tempfile
import zipfile
from pathlib import Path
import cv2
import numpy as np
import tensorflow as tf
from paddleocr import PaddleOCR
from unstructured.partition.image import partition_image

class PDFProcessor:
    def __init__(self):
        # self.ocr = PaddleOCR(lang='sa')
        self.ocr = PaddleOCR(lang='en')
        
    def process_pdf(self, pdf_path):
        """Process PDF and extract images, tables, and text"""
        try:
            # Create temporary directories
            temp_dir = tempfile.mkdtemp()
            self.setup_output_dirs(temp_dir)

            # Process the PDF
            results = self.process_pdf_content(pdf_path)
            
            # Create zip file
            zip_path = os.path.join(temp_dir, "extracted_content.zip")
            self._create_zip(zip_path, [
                self.images_dir, self.tables_dir, self.texts_dir
            ])

            results['zip_path'] = zip_path
            return results

        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    def setup_output_dirs(self, temp_dir):
        """Setup output directories"""
        self.temp_dir = temp_dir
        self.images_dir = os.path.join(temp_dir, "images")
        self.tables_dir = os.path.join(temp_dir, "tables")
        self.texts_dir = os.path.join(temp_dir, "texts")
        self.tables_csv_dir = os.path.join(temp_dir, "tables_csv")
        
        for dir_path in [self.images_dir, self.tables_dir, self.texts_dir, self.tables_csv_dir]:
            os.makedirs(dir_path, exist_ok=True)

    def process_pdf_content(self, pdf_path):
        """Process PDF content using advanced extraction"""
        extracted_images = []
        extracted_tables = []
        extracted_texts = []
        
        with fitz.open(pdf_path) as pdf_document:
            pdf_name = Path(pdf_path).stem
            
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                page_name = f'page_{page_number + 1}'
                
                # Process page content
                page_results = self.process_page(page, page_name, pdf_name)
                
                # Collect results
                extracted_images.extend(page_results.get('images', []))
                extracted_tables.extend(page_results.get('tables', []))
                extracted_texts.extend(page_results.get('texts', []))
                
                print(f"Processed page {page_number + 1}/{pdf_document.page_count}")
        
        return {
            'images': extracted_images,
            'tables': extracted_tables,
            'texts': extracted_texts
        }

    def process_page(self, page, page_name, pdf_name):
        """Process a single page"""
        # Convert PDF page to image
        image_cv = self.convert_page_to_image(page)
        temp_image_path = self.save_temp_image(image_cv)
        
        results = {
            'images': self.extract_page_images(page, page_name),
            'tables': [],
            'texts': []
        }
        
        try:
            # Extract elements using Unstructured
            elements = self.extract_page_elements(temp_image_path)
            
            # Process elements
            for element in elements:
                element_result = self.process_element(element, page_name, pdf_name, image_cv)
                if element_result:
                    element_type = element_result['type']
                    results[element_type].append(element_result['path'])
                    
        finally:
            self.cleanup_temp_file(temp_image_path)
            
        return results

    def convert_page_to_image(self, page, dpi=300):
        """Convert PDF page to image"""
        pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    def save_temp_image(self, image_cv):
        """Save temporary image file"""
        temp_path = os.path.join(self.temp_dir, "temp_page.png")
        cv2.imwrite(temp_path, image_cv)
        return temp_path

    def extract_page_elements(self, image_path):
        """Extract elements from page using Unstructured"""
        elements = partition_image(
            filename=image_path,
            infer_table_structure=True,
            strategy='hi_res'
        )
        return [el.to_dict() for el in elements]

    def process_element(self, element, page_name, pdf_name, image_cv):
        """Process individual elements (text or table) from the page"""
        if element.get("type") == "Table":
            return self.process_table_element(element, page_name, pdf_name, image_cv)
        else:
            return self.process_text_element(element, page_name, pdf_name)

    def process_table_element(self, element, page_name, pdf_name, image_cv):
        """Process a table element"""
        try:
            table_processor = TableProcessor(
                element, page_name, pdf_name, image_cv, 
                self.tables_dir, self.tables_csv_dir, self.ocr
            )
            return table_processor.process()
        except Exception as e:
            print(f"Error processing table: {str(e)}")
            return None

    def process_text_element(self, element, page_name, pdf_name):
        """Process a text element"""
        text_content = element.get("text", "")
        if text_content:
            text_folder = os.path.join(self.texts_dir, f"{pdf_name}-Texts")
            os.makedirs(text_folder, exist_ok=True)
            text_filename = f"{page_name}_text.txt"
            text_path = os.path.join(text_folder, text_filename)
            
            with open(text_path, "a", encoding="utf-8") as text_file:
                text_file.write(text_content + "\n")
            
            return {'type': 'texts', 'path': text_path}
        return None

    def extract_page_images(self, page, page_name):
        """Extract images from a single page"""
        extracted_images = []
        images = page.get_images(full=True)
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            
            image_path = os.path.join(
                self.images_dir,
                f"{page_name}_image_{img_index + 1}.png"
            )
            
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            extracted_images.append(image_path)
            
        return extracted_images

    @staticmethod
    def cleanup_temp_file(temp_path):
        """Clean up temporary files"""
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def _extract_tables(self, pdf_path, output_dir):
        """Extract tables using unstructured and OCR"""
        extracted_tables = []
        pdf_document = fitz.open(pdf_path)
        
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            
            # Convert page to image
            pix = page.get_pixmap(dpi=300, colorspace=fitz.csRGB)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            image_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Save temporary image
            temp_image_path = os.path.join(output_dir, "temp_page.png")
            cv2.imwrite(temp_image_path, image_cv)
            
            try:
                # Extract elements using Unstructured
                elements = partition_image(
                    filename=temp_image_path,
                    infer_table_structure=True,
                    strategy='hi_res'
                )
                
                # Process tables
                table_count = 1
                for element in elements:
                    if element.to_dict().get("type") == "Table":
                        table_processor = TableProcessor(
                            element.to_dict(), 
                            f'page_{page_number + 1}', 
                            Path(pdf_path).stem,
                            image_cv,
                            output_dir,
                            output_dir,
                            self.ocr
                        )
                        result = table_processor.process()
                        if result and result.get('path'):
                            extracted_tables.append(result['path'])
                            table_count += 1
                            
            finally:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
        
        pdf_document.close()
        return extracted_tables

    def _extract_text(self, pdf_path, output_dir):
        """Extract text with positioning and excluding table regions"""
        extracted_texts = []
        pdf_document = fitz.open(pdf_path)
        
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            
            # Convert page to image for table detection
            pix = page.get_pixmap(dpi=300, colorspace=fitz.csRGB)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            image_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Save temporary image
            temp_image_path = os.path.join(output_dir, "temp_page.png")
            cv2.imwrite(temp_image_path, image_cv)
            
            try:
                # Get table regions to exclude
                elements = partition_image(
                    filename=temp_image_path,
                    infer_table_structure=True,
                    strategy='hi_res'
                )
                
                table_regions = []
                for element in elements:
                    if element.to_dict().get("type") == "Table":
                        coords = element.to_dict()["metadata"]["coordinates"]["points"]
                        x_min = min(pt[0] for pt in coords)
                        y_min = min(pt[1] for pt in coords)
                        x_max = max(pt[0] for pt in coords)
                        y_max = max(pt[1] for pt in coords)
                        table_regions.append((x_min, y_min, x_max, y_max))
                
                # Extract text excluding table regions
                text_blocks = []
                for block in page.get_text("blocks"):
                    block_rect = fitz.Rect(block[:4])
                    is_in_table = False
                    
                    for table_region in table_regions:
                        table_rect = fitz.Rect(table_region)
                        if block_rect.intersects(table_rect):
                            is_in_table = True
                            break
                    
                    if not is_in_table:
                        text_blocks.append(block[4])
                
                # Save text content
                text_path = os.path.join(output_dir, f"page_{page_number + 1}.txt")
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(text_blocks))
                extracted_texts.append(text_path)
                
            finally:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
        
        pdf_document.close()
        return extracted_texts

    def _create_zip(self, zip_path, directories):
        """Create ZIP file containing all extracted content"""
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for directory in directories:
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(directory))
                        zipf.write(file_path, arcname)

class TableProcessor:
    """Class to handle table processing"""
    def __init__(self, element, page_name, pdf_name, image_cv, tables_dir, tables_csv_dir, ocr):
        self.element = element
        self.page_name = page_name
        self.pdf_name = pdf_name
        self.image_cv = image_cv
        self.tables_dir = tables_dir
        self.tables_csv_dir = tables_csv_dir
        self.ocr = ocr
        self.setup_directories()

    def setup_directories(self):
        """Setup table directories"""
        self.table_folder = os.path.join(self.tables_dir, f"{self.pdf_name}-Tables")
        self.csv_folder = os.path.join(self.tables_csv_dir, f"{self.pdf_name}-csv")
        os.makedirs(self.table_folder, exist_ok=True)
        os.makedirs(self.csv_folder, exist_ok=True)

    def process(self):
        """Process the table"""
        try:
            # Extract table image
            cropped_table = self.extract_table_image()
            table_path = self.save_table_image(cropped_table)
            
            # Process with OCR
            table_data = self.process_table_ocr(table_path)
            if table_data is None:
                return None
            
            # Save as CSV
            csv_path = self.save_table_csv(table_data)
            
            return {'type': 'tables', 'path': csv_path}
            
        except Exception as e:
            print(f"Error in table processing: {str(e)}")
            return None

    def extract_table_image(self):
        """Extract table image from page"""
        coordinates = self.element["metadata"]["coordinates"]["points"]
        x_min = int(min(pt[0] for pt in coordinates))
        y_min = int(min(pt[1] for pt in coordinates))
        x_max = int(max(pt[0] for pt in coordinates))
        y_max = int(max(pt[1] for pt in coordinates))
        
        # Add padding
        x_min = max(0, x_min - 5)
        y_min = max(0, y_min - 5)
        x_max = min(self.image_cv.shape[1], x_max + 14)
        y_max = min(self.image_cv.shape[0], y_max + 7)
        
        return self.image_cv[y_min:y_max, x_min:x_max]

    def save_table_image(self, cropped_table):
        """Save extracted table image"""
        table_filename = f"{self.page_name}_Table_{len(os.listdir(self.table_folder)) + 1}.png"
        table_path = os.path.join(self.table_folder, table_filename)
        cv2.imwrite(table_path, cropped_table)
        return table_path

    def process_table_ocr(self, table_path):
        """Process table with OCR"""
        output = self.ocr.ocr(table_path)[0]
        if not output:
            return None
            
        return self.restructure_table_data(output, table_path)

    def restructure_table_data(self, output, table_path):
        """Restructure OCR output into table format"""
        # Extract data from OCR output
        boxes = [line[0] for line in output]
        texts = [line[1][0] for line in output]
        probabilities = [line[1][1] for line in output]
        
        # Get table dimensions
        image = cv2.imread(table_path)
        image_height, image_width = image.shape[:2]
        
        # Generate and process boxes
        table_data = self.process_table_boxes(boxes, texts, probabilities, image_width, image_height)
        return table_data

    def process_table_boxes(self, boxes, texts, probabilities, image_width, image_height):
        """Process table boxes and create structured data"""
        horiz_boxes, vert_boxes = self.generate_boxes(boxes, image_width, image_height)
        
        # Apply NMS
        horiz_lines, vert_lines = self.apply_nms(horiz_boxes, vert_boxes, probabilities)
        
        # Create and fill table structure
        return self.create_table_structure(horiz_boxes, vert_boxes, boxes, texts, horiz_lines, vert_lines)

    def generate_boxes(self, boxes, image_width, image_height):
        """Generate horizontal and vertical boxes"""
        horiz_boxes = []
        vert_boxes = []
        
        for box in boxes:
            x_h, x_v = 0, int(box[0][0])
            y_h, y_v = int(box[0][1]), 0
            width_h, width_v = image_width, int(box[2][0] - box[0][0])
            height_h, height_v = int(box[2][1] - box[0][1]), image_height
            
            horiz_boxes.append([x_h, y_h, x_h + width_h, y_h + height_h])
            vert_boxes.append([x_v, y_v, x_v + width_v, y_v + height_v])
            
        return horiz_boxes, vert_boxes

    def apply_nms(self, horiz_boxes, vert_boxes, probabilities):
        """Apply Non-Maximum Suppression"""
        horiz_out = tf.image.non_max_suppression(
            horiz_boxes, probabilities, max_output_size=1000, iou_threshold=0.1
        )
        vert_out = tf.image.non_max_suppression(
            vert_boxes, probabilities, max_output_size=1000, iou_threshold=0.1
        )
        
        return (np.sort(np.array(horiz_out)), np.sort(np.array(vert_out)))

    def create_table_structure(self, horiz_boxes, vert_boxes, boxes, texts, horiz_lines, vert_lines):
        """Create and fill table structure"""
        out_array = [["" for _ in range(len(vert_lines))] for _ in range(len(horiz_lines))]
        unordered_boxes = [vert_boxes[i][0] for i in vert_lines]
        ordered_boxes = np.argsort(unordered_boxes)
        
        for i in range(len(horiz_lines)):
            for j in range(len(vert_lines)):
                resultant = self.intersection(
                    horiz_boxes[horiz_lines[i]], 
                    vert_boxes[vert_lines[ordered_boxes[j]]]
                )
                
                for b in range(len(boxes)):
                    the_box = [boxes[b][0][0], boxes[b][0][1], boxes[b][2][0], boxes[b][2][1]]
                    if self.iou(resultant, the_box) > 0.1:
                        out_array[i][j] = texts[b]
        
        return out_array

    def save_table_csv(self, table_data):
        """Save table data as CSV"""
        csv_filename = f"{self.page_name}_Table_{len(os.listdir(self.csv_folder)) + 1}.csv"
        csv_path = os.path.join(self.csv_folder, csv_filename)
        pd.DataFrame(table_data).to_csv(csv_path, index=False, header=False)
        return csv_path

    @staticmethod
    def intersection(box_1, box_2):
        """Calculate intersection of two boxes"""
        return [box_2[0], box_1[1], box_2[2], box_1[3]]

    @staticmethod
    def iou(box_1, box_2):
        """Calculate Intersection over Union"""
        x_1 = max(box_1[0], box_2[0])
        y_1 = max(box_1[1], box_2[1])
        x_2 = min(box_1[2], box_2[2])
        y_2 = min(box_1[3], box_2[3])
        
        inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1), 0))
        if inter == 0:
            return 0
            
        box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
        box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))
        
        return inter / float(box_1_area + box_2_area - inter) 