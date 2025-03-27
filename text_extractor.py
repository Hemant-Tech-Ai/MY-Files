import os
import numpy as np
from paddleocr import PaddleOCR
import cv2

def extract_text_from_images(input_folder, output_folder="Extracted_Text"):
    """
    Extract text from images using PaddleOCR and save to text files.
    
    Args:
        input_folder (str): Path to folder containing input images
        output_folder (str): Path to save output text files
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Initialize PaddleOCR
    ocr = PaddleOCR(lang='en')
    
    # Get all image files
    image_files = [f for f in os.listdir(input_folder) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))]
    
    print(f"Found {len(image_files)} images to process")
    
    for image_file in image_files:
        image_path = os.path.join(input_folder, image_file)
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error loading image: {image_path}")
            continue
            
        print(f"\nProcessing: {image_file}")
        
        try:
            # Perform OCR
            result = ocr.ocr(image_path)[0]
            
            if not result:
                print(f"No text detected in image: {image_file}")
                continue
            
            # Extract text and confidence scores
            extracted_text = []
            for line in result:
                text = line[1][0]  # Get the text
                confidence = line[1][1]  # Get the confidence score
                box = line[0]  # Get the bounding box coordinates
                
                # Add text with confidence score
                extracted_text.append(f"Text: {text} (Confidence: {confidence:.2f})")
                # Add bounding box coordinates
                extracted_text.append(f"Position: {box}\n")
            
            # Save to text file
            output_filename = f"{os.path.splitext(image_file)[0]}_text.txt"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(extracted_text))
            
            print(f"Text extracted and saved to: {output_filename}")
            
            # Optional: Create visualization of detected text
            vis_image = image.copy()
            for line in result:
                box = np.array(line[0]).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(vis_image, [box], True, (0, 255, 0), 2)
            
            # Save visualization
            vis_filename = f"{os.path.splitext(image_file)[0]}_visualized.png"
            vis_path = os.path.join(output_folder, vis_filename)
            cv2.imwrite(vis_path, vis_image)
            
        except Exception as e:
            print(f"Error processing {image_file}: {str(e)}")
    
    print(f"\nProcessing complete! Extracted text saved in: {output_folder}")

# Example usage
if __name__ == "__main__":
    input_folder = "Input_Images"  # Replace with your input folder path
    extract_text_from_images(input_folder)