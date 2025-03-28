#! pip install transformers>=4.37.0 pillow optimum[onnxruntime]
import os
import time
from PIL import Image
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq
from pathlib import Path
from typing import Optional, Union, List, Tuple, Dict
from contextlib import contextmanager

@contextmanager
def timer(description: str) -> float:
    """Context manager for timing code blocks."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{description}: {elapsed:.3f} seconds")

class FormulaProcessor:
    """A class to process mathematical formulas in images and convert them to LaTeX."""
    
    def __init__(self):
        """Initialize the FormulaProcessor with required models."""
        with timer("Model initialization"):
            self.processor = TrOCRProcessor.from_pretrained('breezedeus/pix2text-mfr')
            self.model = ORTModelForVision2Seq.from_pretrained('breezedeus/pix2text-mfr', use_cache=False)
        self.timing_stats = {
            'total_processing_time': 0.0,
            'image_load_time': 0.0,
            'inference_time': 0.0,
            'processed_images': 0
        }

    def process_single_formula(self, image_path: Union[str, Path]) -> Tuple[Optional[str], Dict[str, float]]:
        """Process a single formula image and return LaTeX with timing information."""
        timing = {'image_load': 0.0, 'inference': 0.0, 'total': 0.0}
        start_total = time.perf_counter()
        
        try:
            # Load and process image
            start_load = time.perf_counter()
            image = Image.open(image_path).convert('RGB')
            timing['image_load'] = time.perf_counter() - start_load
            
            # Generate LaTeX
            start_inference = time.perf_counter()
            pixel_values = self.processor(images=[image], return_tensors="pt").pixel_values
            generated_ids = self.model.generate(pixel_values)
            latex_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            timing['inference'] = time.perf_counter() - start_inference
            
            timing['total'] = time.perf_counter() - start_total
            
            # Update timing statistics
            self.timing_stats['total_processing_time'] += timing['total']
            self.timing_stats['image_load_time'] += timing['image_load']
            self.timing_stats['inference_time'] += timing['inference']
            self.timing_stats['processed_images'] += 1
            
            return latex_text, timing
            
        except Exception as e:
            print(f"Error processing formula image {image_path}: {str(e)}")
            return None, timing

    def process_formula_batch(self, input_folder: Union[str, Path], output_folder: Union[str, Path]) -> List[str]:
        """Process all formula images in a folder and save LaTeX output."""
        batch_start = time.perf_counter()
        
        # Create output folder if it doesn't exist
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Get all image files from input folder
        input_folder = Path(input_folder)
        image_files = list(input_folder.glob("*.png")) + list(input_folder.glob("*.jpg")) + list(input_folder.glob("*.jpeg"))
        
        processed_files = []
        
        # Process each image
        for image_path in image_files:
            latex_text, timing = self.process_single_formula(image_path)
            
            if latex_text:
                # Create output filename (replace image extension with .tex)
                output_path = output_folder / f"{image_path.stem}.tex"
                
                # Save LaTeX to file
                output_path.write_text(latex_text, encoding='utf-8')
                processed_files.append(str(output_path))
                
                print(f"Processed {image_path.name} -> {output_path.name} "
                      f"(load: {timing['image_load']:.3f}s, "
                      f"inference: {timing['inference']:.3f}s, "
                      f"total: {timing['total']:.3f}s)")
        
        batch_time = time.perf_counter() - batch_start
        
        # Print summary statistics
        if self.timing_stats['processed_images'] > 0:
            avg_time = self.timing_stats['total_processing_time'] / self.timing_stats['processed_images']
            print("\nTiming Statistics:")
            print(f"Total batch processing time: {batch_time:.3f} seconds")
            print(f"Average processing time per image: {avg_time:.3f} seconds")
            print(f"Total images processed: {self.timing_stats['processed_images']}")
            print(f"Average image load time: {self.timing_stats['image_load_time'] / self.timing_stats['processed_images']:.3f} seconds")
            print(f"Average inference time: {self.timing_stats['inference_time'] / self.timing_stats['processed_images']:.3f} seconds")
        
        return processed_files

def process_formulas(input_folder: str, output_folder: str, show_progress: bool = True, 
                    parallel: bool = True, max_workers: Optional[int] = None, 
                    use_fast: bool = True) -> Dict[str, float]:
    """Process mathematical formulas from images and convert to LaTeX."""
    processor = FormulaProcessor(use_fast=use_fast)
    return processor.process_formula_batch(  # Changed from process_batch to process_formula_batch
        input_folder=input_folder, 
        output_folder=output_folder
    )

def main():
    # Configure input and output folders
    input_folder = "TEST RESULT 1.0/formulas"
    output_folder = "TEST RESULT 1.1/latex_output"
    
    print(f"Starting formula processing...")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    
    with timer("Total execution"):
        processor = FormulaProcessor()
        processor.process_formula_batch(input_folder, output_folder)

if __name__ == "__main__":
    main()
