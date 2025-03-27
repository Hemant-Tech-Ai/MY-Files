import cv2
import os
from pathlib import Path
import time
import numpy as np
from datetime import timedelta
from typing import List, Dict, Any

from Functions.pdf_partitioner import partition_pdf, _load_pdf_as_images

class PDFElementCropper:
    def __init__(
        self,
        output_dir: str = "Cropped_Elements",
        top_left_padding: int = 10,
        bottom_right_padding: int = 15,
        dpi: int = 300
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.top_left_padding = top_left_padding
        self.bottom_right_padding = bottom_right_padding
        self.dpi = dpi

    def crop_with_padding(self, image, bbox: Dict, output_folder: str, filename: str) -> str:
        """Crop the specified coordinates from the image, apply padding, and save it."""
        # Extract coordinates
        x_min = int(bbox['x1'])
        y_min = int(bbox['y1'])
        x_max = int(bbox['x2'])
        y_max = int(bbox['y2'])

        # Apply top-left and bottom-right padding
        x_min_padded = max(0, x_min - self.top_left_padding)
        y_min_padded = max(0, y_min - self.top_left_padding)
        x_max_padded = min(image.shape[1], x_max + self.bottom_right_padding * 2)
        y_max_padded = min(image.shape[0], y_max + self.bottom_right_padding)

        # Crop the image
        cropped_image = image[y_min_padded:y_max_padded, x_min_padded:x_max_padded]

        # Save cropped image
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, cropped_image)
        print(f"Cropped element saved to: {output_path}")
        return output_path

    def _load_pdf_as_images(self, pdf_path: str) -> List[Any]:
        """Load PDF pages as CV2 images using the pdf_partitioner function."""
        # Get PIL images using the existing function
        pil_images = _load_pdf_as_images(pdf_path, dpi=self.dpi)
        
        # Convert PIL images to CV2 format
        cv2_images = []
        for pil_img in pil_images:
            # Convert PIL image to numpy array
            img_array = np.array(pil_img)
            # Convert RGB to BGR for OpenCV
            cv2_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            cv2_images.append(cv2_img)
        
        return cv2_images

    def process_pdf(self, pdf_path: str):
        """Process a PDF file and crop all detected elements."""
        start_time = time.time()
        
        # Get the PDF filename without extension
        pdf_filename = Path(pdf_path).stem
        
        # Get elements using partition_pdf
        elements = partition_pdf(
            filename=pdf_path,
            dpi=self.dpi
        )
        
        # Convert PDF to images
        page_images = self._load_pdf_as_images(pdf_path)
        
        # Create element type counters
        element_counts = {}
        
        # Process each page
        for page_num, page_image in enumerate(page_images, 1):
            # Get elements for this page
            page_elements = [e for e in elements if e['page_number'] == page_num]
            
            for element in page_elements:
                element_type = element['type']
                
                # Initialize counter for this element type
                if element_type not in element_counts:
                    element_counts[element_type] = 0
                element_counts[element_type] += 1
                
                # Create type-specific output folder
                output_folder = self.output_dir / pdf_filename / element_type
                output_folder.mkdir(parents=True, exist_ok=True)
                
                # Create filename
                filename = f"{pdf_filename}_page{page_num}_{element_type.lower()}_{element_counts[element_type]}.png"
                
                try:
                    # Crop and save the element
                    self.crop_with_padding(
                        image=page_image,
                        bbox=element['bbox'],
                        output_folder=str(output_folder),
                        filename=filename
                    )
                except Exception as e:
                    print(f"Error processing {element_type} on page {page_num}: {str(e)}")
                    continue
        
        # Print summary
        processing_time = time.time() - start_time
        print(f"\nProcessing complete for {pdf_path}")
        print(f"Time taken: {str(timedelta(seconds=round(processing_time)))}")
        print("\nElements extracted:")
        for element_type, count in element_counts.items():
            print(f"  {element_type}: {count}")
        print(f"\nResults saved to: {self.output_dir / pdf_filename}")

def main():
    # Configuration
    INPUT_PDF = "2501.00663v1.pdf"  # Path to your PDF file
    OUTPUT_DIR = "Cropped_Elements"  # Output directory
    DPI = 300
    TOP_LEFT_PADDING = 10
    BOTTOM_RIGHT_PADDING = 15

    try:
        # Initialize cropper
        cropper = PDFElementCropper(
            output_dir=OUTPUT_DIR,
            top_left_padding=TOP_LEFT_PADDING,
            bottom_right_padding=BOTTOM_RIGHT_PADDING,
            dpi=DPI
        )
        
        # Process the PDF
        cropper.process_pdf(INPUT_PDF)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()