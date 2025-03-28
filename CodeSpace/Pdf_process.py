import os
import logging
import warnings
import pandas as pd
import fitz
import cv2
from unstructured.partition.image import partition_image
import numpy as np
import tensorflow as tf
from paddleocr import PaddleOCR

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=info, 2=warning, 3=error

# Suppress PaddleOCR debug messages
logging.getLogger("ppocr").setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

def process_pdf_documents_update(input_dir, output_base_dir, pad_left=5, pad_top=5, pad_right=14, pad_bottom=7, dpi = 300):

# def process_pdf_documents(input_dir, output_base_dir, dpi=300):
    """
    Process PDFs to extract text, tables, embedded images, and create CSV files in a single pass.
    
    Args:
        input_dir (str): Directory containing PDF files
        output_base_dir (str): Base directory for outputs
        dpi (int): DPI for PDF to image conversion
    """
    # Initialize output directories
    text_output_folder = os.path.join(output_base_dir, "Extracted Text")
    tables_output_folder = os.path.join(output_base_dir, "Extracted Tables")
    tables_csv_folder = os.path.join(output_base_dir, "Extracted Tables CSV")
    images_output_folder = os.path.join(output_base_dir, "Extracted Images")
    
    for folder in [text_output_folder, tables_output_folder, tables_csv_folder, images_output_folder]:
        os.makedirs(folder, exist_ok=True)

    def intersection(box_1, box_2):
        """Calculate intersection of two bounding boxes"""
        return [box_2[0], box_1[1], box_2[2], box_1[3]]

    def iou(box_1, box_2):
        """Calculate Intersection over Union of two boxes"""
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

    def extract_embedded_images(pdf_document, page, pdf_name, page_number):
        """Extract embedded images from a PDF page"""
        images_folder = os.path.join(images_output_folder, f"{pdf_name}-images")
        os.makedirs(images_folder, exist_ok=True)
        
        images = page.get_images(full=True)
        print(f"  Page {page_number + 1} has {len(images)} embedded image(s).")

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Construct filename for the image
            image_filename = f"Page_{page_number + 1}_Image_{img_index + 1}.png"
            image_path = os.path.join(images_folder, image_filename)

            # Save the image
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            print(f"    Saved embedded image: {image_path}")

    def process_element(element, page_name, pdf_name, image_cv):
        """Process individual elements (text or table) from the page"""
        if element.get("type") == "Table":
            try:
                coordinates = element["metadata"]["coordinates"]["points"]
                table_folder = os.path.join(tables_output_folder, f"{pdf_name}-Tables")
                csv_folder = os.path.join(tables_csv_folder, f"{pdf_name}-csv")
                
                # Create necessary folders
                os.makedirs(table_folder, exist_ok=True)
                os.makedirs(csv_folder, exist_ok=True)
                
                # Crop and save table image
                x_min = int(min(pt[0] for pt in coordinates))
                y_min = int(min(pt[1] for pt in coordinates))
                x_max = int(max(pt[0] for pt in coordinates))
                y_max = int(max(pt[1] for pt in coordinates))
                
                # Add padding
                x_min = max(0, x_min - pad_left)
                y_min = max(0, y_min - pad_top)
                x_max = min(image_cv.shape[1], x_max + pad_right)
                y_max = min(image_cv.shape[0], y_max + pad_bottom)
                
                cropped_table = image_cv[y_min:y_max, x_min:x_max]
                table_filename = f"{page_name}_Table_{len(os.listdir(table_folder)) + 1}.png"
                table_path = os.path.join(table_folder, table_filename)
                cv2.imwrite(table_path, cropped_table)
                print(f"Cropped table saved to: {table_path}")
                
                # Process table with OCR and restructure
                output = ocr.ocr(table_path)[0]
                if not output:
                    print(f"No OCR output for table: {table_filename}")
                    return

                # Extract bounding boxes and text
                boxes = [line[0] for line in output]
                texts = [line[1][0] for line in output]
                probabilities = [line[1][1] for line in output]

                # Generate horizontal and vertical boxes
                image_height, image_width = cropped_table.shape[:2]
                horiz_boxes = []
                vert_boxes = []

                for box in boxes:
                    x_h, x_v = 0, int(box[0][0])
                    y_h, y_v = int(box[0][1]), 0
                    width_h, width_v = image_width, int(box[2][0] - box[0][0])
                    height_h, height_v = int(box[2][1] - box[0][1]), image_height

                    horiz_boxes.append([x_h, y_h, x_h + width_h, y_h + height_h])
                    vert_boxes.append([x_v, y_v, x_v + width_v, y_v + height_v])

                # Apply NMS
                horiz_out = tf.image.non_max_suppression(
                    horiz_boxes, probabilities, max_output_size=1000, iou_threshold=0.1
                )
                vert_out = tf.image.non_max_suppression(
                    vert_boxes, probabilities, max_output_size=1000, iou_threshold=0.1
                )

                horiz_lines = np.sort(np.array(horiz_out))
                vert_lines = np.sort(np.array(vert_out))

                # Create table structure
                out_array = [["" for _ in range(len(vert_lines))] for _ in range(len(horiz_lines))]
                unordered_boxes = [vert_boxes[i][0] for i in vert_lines]
                ordered_boxes = np.argsort(unordered_boxes)

                # Fill table with text
                for i in range(len(horiz_lines)):
                    for j in range(len(vert_lines)):
                        resultant = intersection(
                            horiz_boxes[horiz_lines[i]], 
                            vert_boxes[vert_lines[ordered_boxes[j]]]
                        )

                        for b in range(len(boxes)):
                            the_box = [boxes[b][0][0], boxes[b][0][1], boxes[b][2][0], boxes[b][2][1]]
                            if iou(resultant, the_box) > 0.1:
                                out_array[i][j] = texts[b]

                # Save as CSV
                csv_filename = f"{os.path.splitext(table_filename)[0]}.csv"
                csv_path = os.path.join(csv_folder, csv_filename)
                pd.DataFrame(out_array).to_csv(csv_path, index=False, header=False)
                print(f"Saved CSV: {csv_filename} in {csv_folder}")
                
            except (KeyError, IndexError) as e:
                print(f"Error processing table: {e}")
                
        elif element.get("type") != "Table":
            # Handle text element
            text_content = element.get("text", "")
            if text_content:
                text_folder = os.path.join(text_output_folder, f"{pdf_name}-Texts")
                os.makedirs(text_folder, exist_ok=True)
                text_filename = f"{page_name}_text.txt"
                text_path = os.path.join(text_folder, text_filename)
                
                with open(text_path, "a", encoding="utf-8") as text_file:
                    text_file.write(text_content + "\n")

    # Initialize OCR
    ocr = PaddleOCR(lang='en')
    
    # Process each PDF
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files to process")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        print(f"\nProcessing PDF: {pdf_file}")
        
        pdf_document = fitz.open(pdf_path)
        
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            page_name = f'page_{page_number + 1}'
            
            # Extract embedded images first
            extract_embedded_images(pdf_document, page, pdf_name, page_number)
            
            # Convert PDF page to image for text and table extraction
            pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            image_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Create temporary image file
            temp_image_path = os.path.join(output_base_dir, "temp_page.png")
            cv2.imwrite(temp_image_path, image_cv)
            
            try:
                # Extract elements using Unstructured
                elements = partition_image(filename=temp_image_path, 
                                        infer_table_structure=True, 
                                        strategy='hi_res')
                element_dict = [el.to_dict() for el in elements]
                
                # Process each element
                for element in element_dict:
                    process_element(element, page_name, pdf_name, image_cv)
                    
            finally:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
            
            print(f"Processed page {page_number + 1}/{pdf_document.page_count}")
        
        pdf_document.close()
        print(f"Finished processing PDF: {pdf_file}")

    print("\nProcessing complete!")
    print(f"Text extracted to: {text_output_folder}")
    print(f"Tables extracted to: {tables_output_folder}")
    print(f"Table CSVs saved to: {tables_csv_folder}")
    print(f"Embedded images extracted to: {images_output_folder}")

input_directory = "TEST INPUT PDF"
output_dir = "TEST_RESULT_1"
pad_left=5
pad_top=5
pad_right=20
pad_bottom=7

# process_pdf_documents(input_directory, output_dir)
process_pdf_documents_update(input_directory, output_dir, pad_left, pad_top, pad_right, pad_bottom)