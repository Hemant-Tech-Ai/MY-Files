#!/usr/bin/env python3
"""
PDF Element Detection and Cropping Tool using OpenCV

This script uses OpenCV for image processing and cropping of detected elements in PDFs.
It provides enhanced image processing capabilities and better quality crops.
"""

import os
# import io
import sys
import argparse
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from PIL import Image as PILImage
from pathlib import Path

from Functions.filetype import detect_filetype, FileType
from Functions.pdfminer_utiles import PDFMinerConfig
from Functions.utiles import requires_dependencies


class PDFElementDetectorCV2:
    """
    Enhanced PDF element detector using OpenCV for image processing.
    Provides better quality crops and additional image processing capabilities.
    """
    
    def __init__(
        self,
        hi_res_model_name: Optional[str] = "yolox",
        dpi: int = 300,
        languages: List[str] = ["eng"],
        pdfminer_config: Optional[PDFMinerConfig] = None,
        output_dir: str = "output",
        padding: int = 5  # Padding around detected elements
    ):
        """
        Initialize the PDF element detector with OpenCV support.
        
        Args:
            hi_res_model_name: Name of the high-resolution model for layout detection
            dpi: DPI for PDF rendering (higher values give better detection)
            languages: List of languages to process
            pdfminer_config: Optional PDFMiner configuration
            output_dir: Directory for saving extracted elements
            padding: Padding pixels around detected elements
        """
        self.hi_res_model_name = hi_res_model_name
        self.dpi = dpi
        self.languages = languages
        self.pdfminer_config = pdfminer_config or PDFMinerConfig()
        self.output_dir = Path(output_dir)
        self.padding = padding
        
        # Color mapping for visualization
        self.color_map = {
            "Title": (0, 0, 255),       # Red (BGR)
            "NarrativeText": (255, 0, 0), # Blue (BGR)
            "Text": (255, 0, 0),        # Blue (BGR)
            "Table": (0, 255, 0),       # Green (BGR)
            "Image": (128, 0, 128),     # Purple (BGR)
            "ListItem": (0, 165, 255),  # Orange (BGR)
            "FigureCaption": (128, 128, 0),  # Teal (BGR)
            "Formula": (255, 0, 255),   # Magenta (BGR)
            "Unknown": (128, 128, 128)  # Gray (BGR)
        }
    
    @requires_dependencies("Functions.Inferences.yolox")
    def _load_detection_model(self):
        """Load the YOLOX detection model."""


        from Functions.base import get_model


        return get_model("yolox")
    
    def _verify_pdf(self, file_or_path) -> tuple[str, bytes]:
        """Verify PDF file and return path and bytes."""
        if isinstance(file_or_path, str):
            if not os.path.exists(file_or_path):
                raise FileNotFoundError(f"File not found: {file_or_path}")
            
            file_type = detect_filetype(file_path=file_or_path)
            if file_type != FileType.PDF:
                raise ValueError(f"File is not a PDF: {file_or_path}")
            
            with open(file_or_path, "rb") as f:
                file_bytes = f.read()
            return file_or_path, file_bytes
        else:
            file_bytes = file_or_path.read()
            file_or_path.seek(0)
            return "", file_bytes
    
    def _pdf_to_cv2_images(self, pdf_path: str, pdf_bytes: bytes) -> List[np.ndarray]:
        """
        Convert PDF pages to OpenCV images.
        
        Args:
            pdf_path: Path to PDF file
            pdf_bytes: PDF file bytes
            
        Returns:
            List of OpenCV images (numpy arrays)
        """
        import fitz
        
        doc = fitz.open(pdf_path) if pdf_path else fitz.open(stream=pdf_bytes, filetype="pdf")
        zoom = self.dpi / 72
        images = []
        
        for page in doc:
            matrix = fitz.Matrix(zoom, zoom)
            pixmap = page.get_pixmap(matrix=matrix)
            
            # Convert to numpy array directly
            img_array = np.frombuffer(pixmap.samples, dtype=np.uint8)
            img_array = img_array.reshape((pixmap.height, pixmap.width, 3))
            
            # Convert RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            images.append(img_bgr)
        
        doc.close()
        return images
    
    def detect_elements(self, file_or_path) -> List[Dict[str, Any]]:
        """
        Detect and classify elements in a PDF document.
        
        Args:
            file_or_path: PDF file path or file-like object
            
        Returns:
            List of detected elements with their properties
        """


        from Functions.Inferences.layoutelement import LayoutElements


        
        pdf_path, pdf_bytes = self._verify_pdf(file_or_path)
        page_images = self._pdf_to_cv2_images(pdf_path, pdf_bytes)
        
        if not page_images:
            raise ValueError("No pages rendered from the PDF")
        
        model = self._load_detection_model()
        all_elements = []
        
        for idx, page_image in enumerate(page_images, 1):
            # Convert BGR to RGB for the model
            rgb_image = cv2.cvtColor(page_image, cv2.COLOR_BGR2RGB)
            pil_image = PILImage.fromarray(rgb_image)
            
            predictions = model.predict(pil_image)
            
            if predictions is None:
                print(f"Warning: No predictions for page {idx}")
                continue
            
            page_elements = (
                list(predictions.iter_elements())
                if isinstance(predictions, LayoutElements)
                else predictions if isinstance(predictions, list)
                else predictions.elements if hasattr(predictions, 'elements')
                else predictions.as_list() if hasattr(predictions, 'as_list')
                else []
            )
            
            for element in page_elements:
                if not hasattr(element, 'bbox') or element.bbox is None:
                    continue
                
                element_info = {
                    "type": element.type if hasattr(element, 'type') and element.type else "Unknown",
                    "page_number": idx,
                    "coordinates": {
                        "bbox": [
                            element.bbox.x1,
                            element.bbox.y1,
                            element.bbox.x2,
                            element.bbox.y2
                        ]
                    },
                    "confidence": element.prob if hasattr(element, 'prob') else None,
                    "text": element.text if hasattr(element, 'text') else None
                }
                all_elements.append(element_info)
        
        return all_elements
    
    def crop_element_cv2(self, image: np.ndarray, bbox: List[float], padding: int = None) -> np.ndarray:
        """
        Crop an element from an image using OpenCV with optional padding and preprocessing.
        
        Args:
            image: OpenCV image (numpy array)
            bbox: Bounding box coordinates [x1, y1, x2, y2]
            padding: Optional padding around the element
            
        Returns:
            Cropped OpenCV image
        """
        if padding is None:
            padding = self.padding
        
        height, width = image.shape[:2]
        
        # Add padding and ensure coordinates are within image bounds
        x1 = max(0, int(bbox[0] - padding))
        y1 = max(0, int(bbox[1] - padding))
        x2 = min(width, int(bbox[2] + padding))
        y2 = min(height, int(bbox[3] + padding))
        
        if x1 >= x2 or y1 >= y2:
            raise ValueError(f"Invalid bounding box after padding: [{x1}, {y1}, {x2}, {y2}]")
        
        # Crop the region
        cropped = image[y1:y2, x1:x2]
        
        # Optional: Apply image enhancement
        # cropped = cv2.fastNlMeansDenoisingColored(cropped)  # Denoise
        # cropped = cv2.detailEnhance(cropped)  # Enhance details
        
        return cropped
    
    def extract_elements_cv2(self, file_or_path, types_to_extract: List[str] = None):
        """
        Extract and save elements using OpenCV for better quality.
        
        Args:
            file_or_path: PDF file path or file-like object
            types_to_extract: List of element types to extract
        """
        if types_to_extract is None:
            types_to_extract = ["Table", "Formula", "Picture"]
        
        self.output_dir.mkdir(exist_ok=True)
        type_dirs = {}
        for elem_type in types_to_extract:
            type_dir = self.output_dir / elem_type.lower()
            type_dir.mkdir(exist_ok=True)
            type_dirs[elem_type] = type_dir
        
        detections = self.detect_elements(file_or_path)
        filtered_detections = [d for d in detections if d.get("type") in types_to_extract]
        
        if not filtered_detections:
            print(f"No elements of types {types_to_extract} found")
            return {}
        
        pdf_path, pdf_bytes = self._verify_pdf(file_or_path)
        pdf_filename = Path(pdf_path).stem if pdf_path else "document"
        page_images = self._pdf_to_cv2_images(pdf_path, pdf_bytes)
        
        saved_files = {elem_type: [] for elem_type in types_to_extract}
        
        for page_num, page_image in enumerate(page_images, 1):
            page_elements = [d for d in filtered_detections if d.get("page_number") == page_num]
            
            for i, element in enumerate(page_elements):
                bbox = element.get("coordinates", {}).get("bbox")
                if not bbox:
                    continue
                
                elem_type = element.get("type")
                try:
                    # Crop using OpenCV
                    cropped = self.crop_element_cv2(page_image, bbox)
                    
                    # Save the cropped image
                    filename = f"{pdf_filename}_page{page_num}_{elem_type.lower()}_{i+1}.png"
                    save_path = type_dirs[elem_type] / filename
                    
                    cv2.imwrite(str(save_path), cropped)
                    saved_files[elem_type].append(str(save_path))
                    print(f"Saved {elem_type} element to {save_path}")
                    
                except Exception as e:
                    print(f"Warning: Failed to crop element on page {page_num}: {str(e)}")
                    continue
        
        # Print summary
        for elem_type, files in saved_files.items():
            print(f"Extracted {len(files)} {elem_type} elements")
        
        return saved_files
    
    def visualize_detections_cv2(self, file_or_path, output_path: str = "detections.png"):
        """
        Visualize detected elements using OpenCV.
            
            Args:
            file_or_path: PDF file path or file-like object
            output_path: Path to save visualization
        """
        detections = self.detect_elements(file_or_path)
        pdf_path, pdf_bytes = self._verify_pdf(file_or_path)
        page_images = self._pdf_to_cv2_images(pdf_path, pdf_bytes)
        
        if not page_images:
            raise ValueError("No pages rendered from the PDF")
        
        # Group detections by page
        detections_by_page = {}
        for detection in detections:
            page_num = detection.get("page_number", 1)
            if page_num not in detections_by_page:
                detections_by_page[page_num] = []
            detections_by_page[page_num].append(detection)
        
        # Process each page
        annotated_images = []
        for page_num, page_image in enumerate(page_images, 1):
            page_detections = detections_by_page.get(page_num, [])
            
            # Create a copy for drawing
            annotated = page_image.copy()
            
            # Draw each detection
            for detection in page_detections:
                elem_type = detection.get("type", "Unknown")
                bbox = detection.get("coordinates", {}).get("bbox")
                
                if not bbox:
                    continue
                
                # Get color for element type
                color = self.color_map.get(elem_type, (128, 128, 128))
                
                # Draw rectangle
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                
                # Add label
                label = f"{elem_type}"
                cv2.putText(
                    annotated,
                    label,
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )
            
            annotated_images.append(annotated)
        
        # Save visualizations
        if len(annotated_images) == 1:
            cv2.imwrite(output_path, annotated_images[0])
        else:
            base, ext = os.path.splitext(output_path)
            for i, img in enumerate(annotated_images):
                page_path = f"{base}_page{i+1}{ext}"
                cv2.imwrite(page_path, img)
        
        return annotated_images


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Detect and extract elements from PDF documents using OpenCV"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--dpi", type=int, default=300,
                      help="DPI for PDF rendering (default: 300)")
    parser.add_argument("--filter-types", "-f", nargs="+",
                      help="Filter by element types (e.g., 'Table Formula')")
    parser.add_argument("--output-dir", "-o", default="output",
                      help="Output directory for extracted elements")
    parser.add_argument("--extract", "-e", action="store_true",
                      help="Extract detected elements as images")
    parser.add_argument("--padding", "-p", type=int, default=5,
                      help="Padding around extracted elements (default: 5)")
    parser.add_argument("--visualize", "-v", action="store_true",
                      help="Create visualization of detected elements")
    
    args = parser.parse_args()
    
    # Verify PDF exists
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    
    try:
        # Initialize detector
        detector = PDFElementDetectorCV2(
            dpi=args.dpi,
            output_dir=args.output_dir,
            padding=args.padding
        )
        
        # Process the PDF
        print(f"Processing {pdf_path}...")
        
        # Extract elements if requested
        if args.extract:
            print("\nExtracting elements...")
            detector.extract_elements_cv2(
                str(pdf_path),
                types_to_extract=args.filter_types
            )
        
        # Create visualization if requested
        if args.visualize:
            print("\nCreating visualization...")
            detector.visualize_detections_cv2(
                str(pdf_path),
                output_path=str(Path(args.output_dir) / "detections.png")
            )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 