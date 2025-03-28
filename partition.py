import time
import os
import numpy as np
import pandas as pd
import cv2
from pathlib import Path
from paddleocr import PaddleOCR
from Functions.pdf_partitioner import partition_pdf, _load_pdf_as_images
from crop_elements import PDFElementCropper
from formula import FormulaProcessor

def intersection(box1, box2):
    """Calculate intersection of two boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    if x2 < x1 or y2 < y1:
        return [0, 0, 0, 0]
    return [x1, y1, x2, y2]

def iou(box1, box2):
    """Calculate Intersection over Union of two boxes."""
    inter_box = intersection(box1, box2)
    inter_area = max(0, inter_box[2] - inter_box[0]) * max(0, inter_box[3] - inter_box[1])
    
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    iou = inter_area / (area1 + area2 - inter_area + 1e-6)
    return iou

def non_max_suppression(boxes, scores, iou_threshold):
    """Apply non-maximum suppression to boxes.
    
    Args:
        boxes: List of boxes [x1, y1, x2, y2]
        scores: List of confidence scores
        iou_threshold: IoU threshold for suppression
        
    Returns:
        List of indices of selected boxes
    """
    if not boxes:
        return []
    
    # Convert to numpy arrays
    boxes = np.array(boxes)
    scores = np.array(scores)
    
    # Sort by score
    idxs = np.argsort(scores)
    pick = []
    
    while len(idxs) > 0:
        # Pick the last box (highest score)
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        
        # Find IoU with rest of the boxes
        overlap = np.array([iou(boxes[i], boxes[idxs[idx]]) for idx in range(last)])
        
        # Remove boxes with IoU > threshold
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > iou_threshold)[0])))
    
    return pick

def process_table_with_ocr(table_path: str, output_dir: str) -> None:
    """Process a table image with OCR and save as CSV.
    
    Args:
        table_path: Path to the table image
        output_dir: Directory to save CSV output
    """
    try:
        # Initialize OCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
        # Create output directory for CSVs
        csv_folder = os.path.join(output_dir, 'csv_tables')
        os.makedirs(csv_folder, exist_ok=True)
        
        # Run OCR
        output = ocr.ocr(table_path)[0]
        if not output:
            print(f"No OCR output for table: {os.path.basename(table_path)}")
            return

        # Extract bounding boxes and text
        boxes = [line[0] for line in output]
        texts = [line[1][0] for line in output]
        probabilities = [line[1][1] for line in output]

        # Load image to get dimensions
        image = cv2.imread(table_path)
        image_height, image_width = image.shape[:2]
        
        # Generate horizontal and vertical boxes
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
        horiz_out = non_max_suppression(horiz_boxes, probabilities, iou_threshold=0.1)
        vert_out = non_max_suppression(vert_boxes, probabilities, iou_threshold=0.1)

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
        table_filename = os.path.basename(table_path)
        csv_filename = f"{os.path.splitext(table_filename)[0]}.csv"
        csv_path = os.path.join(csv_folder, csv_filename)
        pd.DataFrame(out_array).to_csv(csv_path, index=False, header=False)
        print(f"Saved CSV: {csv_filename} in {csv_folder}")
        
    except Exception as e:
        print(f"Error processing table {table_path}: {str(e)}")

def process_formula_with_ocr(formula_path: str, output_dir: str) -> None:
    """Process a formula image and convert to LaTeX.
    
    Args:
        formula_path: Path to the formula image
        output_dir: Directory to save LaTeX output
    """
    try:
        # Initialize formula processor
        processor = FormulaProcessor()
        
        # Create output directory for LaTeX files
        latex_folder = os.path.join(output_dir, 'latex_formulas')
        os.makedirs(latex_folder, exist_ok=True)
        
        # Process formula
        latex_text = processor.process_single_formula(formula_path)
        if latex_text:
            # Create output filename
            formula_filename = os.path.basename(formula_path)
            latex_filename = f"{os.path.splitext(formula_filename)[0]}.tex"
            latex_path = os.path.join(latex_folder, latex_filename)
            
            # Save LaTeX
            with open(latex_path, 'w', encoding='utf-8') as f:
                f.write(latex_text)
            print(f"Saved LaTeX: {latex_filename} in {latex_folder}")
        else:
            print(f"No LaTeX output for formula: {os.path.basename(formula_path)}")
            
    except Exception as e:
        print(f"Error processing formula {formula_path}: {str(e)}")

def main():
    # Configuration - edit these values
    input_pdf = "2501.00663v1.pdf"  # Path to the input PDF file
    output_dir = "extracted_elements1"  # Base output directory
    
    # Initialize cropper
    cropper = PDFElementCropper(
        output_dir=output_dir,
        top_left_padding=10,
        bottom_right_padding=15,
        dpi=300
    )

    # Record the start time
    start_time = time.time()

    try:
        # Process PDF and get cropped elements
        element_counts, elements_dir = cropper.process_pdf(input_pdf)
        
        # Process tables with OCR
        tables_dir = elements_dir / "Table"
        if tables_dir.exists():
            print("\nProcessing tables with OCR...")
            for table_file in tables_dir.glob("*.png"):
                print(f"\nProcessing table: {table_file.name}")
                process_table_with_ocr(str(table_file), str(elements_dir))
        
        # Process formulas with OCR
        formulas_dir = elements_dir / "Formula"
        if formulas_dir.exists():
            print("\nProcessing formulas with OCR...")
            for formula_file in formulas_dir.glob("*.png"):
                print(f"\nProcessing formula: {formula_file.name}")
                process_formula_with_ocr(str(formula_file), str(elements_dir))
        
        # Record the end time and print summary
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("\nProcessing Summary:")
        print(f"Total processing time: {elapsed_time:.2f} seconds")
        print("Elements extracted:")
        for element_type, count in element_counts.items():
            print(f"  {element_type}: {count}")
        print(f"\nResults saved in: {elements_dir}")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")

if __name__ == "__main__":
    main()