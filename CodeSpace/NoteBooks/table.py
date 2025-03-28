import os
import pandas as pd
import cv2
import numpy as np
from paddleocr import PaddleOCR

def create_test_image(filename="test_tables/sample_table.png"):
    """Create a sample table image for testing purposes"""
    # Create a blank white image
    height, width = 500, 800
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw table grid
    # Vertical lines
    for x in range(100, width, 140):
        cv2.line(img, (x, 50), (x, 350), (0, 0, 0), 2)
    
    # Horizontal lines
    for y in range(50, 400, 60):
        cv2.line(img, (100, y), (660, y), (0, 0, 0), 2)
    
    # Add text to cells
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Header row
    cv2.putText(img, "Name", (120, 90), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Age", (260, 90), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "City", (400, 90), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Occupation", (540, 90), font, 0.7, (0, 0, 0), 2)
    
    # Data rows
    cv2.putText(img, "John", (120, 150), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "35", (260, 150), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "New York", (400, 150), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Engineer", (540, 150), font, 0.7, (0, 0, 0), 2)
    
    cv2.putText(img, "Mary", (120, 210), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "28", (260, 210), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Boston", (400, 210), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Designer", (540, 210), font, 0.7, (0, 0, 0), 2)
    
    cv2.putText(img, "Robert", (120, 270), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "42", (260, 270), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Chicago", (400, 270), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Doctor", (540, 270), font, 0.7, (0, 0, 0), 2)
    
    cv2.putText(img, "Lisa", (120, 330), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "31", (260, 330), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Miami", (400, 330), font, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Teacher", (540, 330), font, 0.7, (0, 0, 0), 2)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save the image
    cv2.imwrite(filename, img)
    print(f"Created test image: {filename}")

def extract_tables_from_images(image_folder, output_folder="Extracted Tables"):

    ocr = PaddleOCR(lang='en')

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Function to compute intersection of two bounding boxes
    def intersection(box_1, box_2):
        return [box_2[0], box_1[1], box_2[2], box_1[3]]

    # Function to compute IoU (Intersection over Union)
    def iou(box_1, box_2):
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
        
    # Non-Maximum Suppression implementation
    def non_max_suppression(boxes, scores, threshold):
        if len(boxes) == 0:
            return []
            
        boxes = np.array(boxes)
        
        # Initialize the list of picked indexes
        pick = []
        
        # Coordinates of bounding boxes
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        
        # Compute the area of the bounding boxes
        area = (x2 - x1) * (y2 - y1)
        
        # Sort by scores (if provided) or by the bottom-right y-coordinate
        if scores is not None:
            idxs = np.argsort(scores)
        else:
            idxs = np.argsort(y2)
        
        # Keep looping while some indexes still remain in the indexes list
        while len(idxs) > 0:
            # Grab the last index in the indexes list and add the index to the list of picked indexes
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            
            # Find the largest (x, y) coordinates for the start of the bounding box
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            
            # Find the smallest (x, y) coordinates for the end of the bounding box
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])
            
            # Compute the width and height of the bounding box
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            
            # Compute the ratio of overlap
            overlap = (w * h) / area[idxs[:last]]
            
            # Delete all indexes from the index list that have an overlap greater than the threshold
            idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > threshold)[0])))
            
        # Return only the bounding boxes that were picked
        return pick

    # Get all image files from the folder
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Process each image
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        image_cv = cv2.imread(image_path)

        # Ensure the image was loaded correctly
        if image_cv is None:
            print(f"Error loading image: {image_path}")
            continue

        image_height, image_width = image_cv.shape[:2]

        # Perform OCR
        output = ocr.ocr(image_path)[0]

        # Extract bounding boxes, detected text, and confidence scores
        boxes = [line[0] for line in output]
        texts = [line[1][0] for line in output]
        probabilities = [line[1][1] for line in output]

        # Copy image for processing
        im = image_cv.copy()

        horiz_boxes = []
        vert_boxes = []

        # Generate horizontal and vertical bounding boxes
        for box in boxes:
            x_h, x_v = 0, int(box[0][0])
            y_h, y_v = int(box[0][1]), 0
            width_h, width_v = image_width, int(box[2][0] - box[0][0])
            height_h, height_v = int(box[2][1] - box[0][1]), image_height

            horiz_boxes.append([x_h, y_h, x_h + width_h, y_h + height_h])
            vert_boxes.append([x_v, y_v, x_v + width_v, y_v + height_v])

            cv2.rectangle(im, (x_h, y_h), (x_h + width_h, y_h + height_h), (0, 0, 255), 1)
            cv2.rectangle(im, (x_v, y_v), (x_v + width_v, y_v + height_v), (0, 255, 0), 1)

        # Apply Non-Maximum Suppression (NMS) for horizontal boxes
        horiz_lines = non_max_suppression(horiz_boxes, probabilities, 0.1)
        horiz_lines = np.sort(np.array(horiz_lines))

        im_nms = image_cv.copy()

        for val in horiz_lines:
            cv2.rectangle(im_nms, (int(horiz_boxes[val][0]), int(horiz_boxes[val][1])),
                          (int(horiz_boxes[val][2]), int(horiz_boxes[val][3])), (0, 0, 255), 1)

        # Apply Non-Maximum Suppression (NMS) for vertical boxes
        vert_lines = non_max_suppression(vert_boxes, probabilities, 0.1)
        vert_lines = np.sort(np.array(vert_lines))

        for val in vert_lines:
            cv2.rectangle(im_nms, (int(vert_boxes[val][0]), int(vert_boxes[val][1])),
                          (int(vert_boxes[val][2]), int(vert_boxes[val][3])), (255, 0, 0), 1)

        # Create an empty table structure
        out_array = [["" for _ in range(len(vert_lines))] for _ in range(len(horiz_lines))]

        # Sort bounding boxes based on vertical position
        unordered_boxes = [vert_boxes[i][0] for i in vert_lines]
        ordered_boxes = np.argsort(unordered_boxes)

        # Fill the table using intersection and IoU logic
        for i in range(len(horiz_lines)):
            for j in range(len(vert_lines)):
                resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[ordered_boxes[j]]])

                for b in range(len(boxes)):
                    the_box = [boxes[b][0][0], boxes[b][0][1], boxes[b][2][0], boxes[b][2][1]]
                    if iou(resultant, the_box) > 0.1:
                        out_array[i][j] = texts[b]

        # Convert to a structured array
        out_array = np.array(out_array)

        # Save extracted text and structure as a CSV file with the image filename
        csv_filename = f"{os.path.splitext(image_file)[0]}.csv"
        csv_output_path = os.path.join(output_folder, csv_filename)
        pd.DataFrame(out_array).to_csv(csv_output_path, index=False, header=False)

        print(f"Processing completed for {image_file}. Results saved in {output_folder}")

    print("\n All images processed successfully! Extracted tables saved in:", output_folder)

# Create a test image
create_test_image()

input_directory = "test_tables"
output_directory = "extracted_tables"

extract_tables_from_images(input_directory, output_directory)