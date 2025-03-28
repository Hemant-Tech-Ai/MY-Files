#! pip install transformers>=4.37.0 pillow optimum[onnxruntime] tqdm
import os
import time
import logging
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
from PIL import Image
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq

# Configure logging
def setup_logging(log_file="formula_processing.log"):
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("FormulaProcessor")

# Initialize logger at module level but allow reconfiguration
logger = setup_logging()

def time_function(description: str, func, *args, **kwargs):
    """Execute a function and time it."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    logger.info(f"{description}: {elapsed:.3f} seconds")
    return result, elapsed

class FormulaProcessor:
    """Class for processing mathematical formulas in images to LaTeX"""
    
    def __init__(self, model_name='breezedeus/pix2text-mfr', use_fast=True):
        """Initialize the processor with the specified model"""
        self.model_name = model_name
        self.use_fast = use_fast
        self.processor = None
        self.model = None
        self.stats = {
            'total_time': 0.0,
            'model_init_time': 0.0,
            'image_load_time': 0.0,
            'inference_time': 0.0,
            'file_write_time': 0.0,
            'images_processed': 0,
            'images_failed': 0
        }
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the OCR processor and model"""
        logger.info(f"Initializing model and processor ({self.model_name})...")
        start_init = time.perf_counter()
        self.processor = TrOCRProcessor.from_pretrained(self.model_name, use_fast=self.use_fast)
        self.model = ORTModelForVision2Seq.from_pretrained(self.model_name, use_cache=False)
        self.stats['model_init_time'] = time.perf_counter() - start_init
        logger.info(f"Model initialization: {self.stats['model_init_time']:.3f} seconds")
    
    def process_single_image(self, image_path: str, output_path: Optional[str] = None) -> Tuple[str, Dict[str, float]]:
        """
        Process a single formula image and return LaTeX text
        
        Args:
            image_path: Path to image file
            output_path: Optional path to save LaTeX output
            
        Returns:
            Tuple of (LaTeX text, timing dictionary)
        """
        timing = {'load': 0.0, 'inference': 0.0, 'write': 0.0, 'total': 0.0}
        start_total = time.perf_counter()
        
        try:
            # Load and process image
            start_load = time.perf_counter()
            image = Image.open(image_path).convert('RGB')
            timing['load'] = time.perf_counter() - start_load
            self.stats['image_load_time'] += timing['load']
            
            # Generate LaTeX
            start_inference = time.perf_counter()
            pixel_values = self.processor(images=[image], return_tensors="pt").pixel_values
            generated_ids = self.model.generate(pixel_values)
            latex_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            timing['inference'] = time.perf_counter() - start_inference
            self.stats['inference_time'] += timing['inference']
            
            # Save LaTeX to file if output path is provided
            if output_path:
                start_write = time.perf_counter()
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(latex_text)
                timing['write'] = time.perf_counter() - start_write
                self.stats['file_write_time'] += timing['write']
                
            timing['total'] = time.perf_counter() - start_total
            self.stats['images_processed'] += 1
            
            # Log success with timing details
            filename = os.path.basename(image_path)
            logger.info(f"Processed {filename} "
                      f"(load: {timing['load']:.3f}s, "
                      f"inference: {timing['inference']:.3f}s, "
                      f"write: {timing['write']:.3f}s, "
                      f"total: {timing['total']:.3f}s)")
                
            return latex_text, timing
            
        except Exception as e:
            logger.error(f"Error processing {image_path}: {str(e)}")
            self.stats['images_failed'] += 1
            return None, timing
    
    def _process_image_worker(self, args):
        """Worker function for parallel processing"""
        image_file, input_folder, output_folder = args
        image_path = os.path.join(input_folder, image_file)
        output_filename = os.path.splitext(image_file)[0] + '.tex'
        output_path = os.path.join(output_folder, output_filename)
        return self.process_single_image(image_path, output_path)
    
    def process_batch(self, input_folder: str, output_folder: str, show_progress: bool = True, 
                     parallel: bool = True, max_workers: Optional[int] = None) -> Dict[str, float]:
        """
        Process all formula images in a folder and save LaTeX output
        
        Args:
            input_folder: Path to folder containing formula images
            output_folder: Path to save LaTeX output files
            show_progress: Whether to show a progress bar
            parallel: Whether to process images in parallel
            max_workers: Maximum number of parallel workers (None = auto)
            
        Returns:
            Dictionary containing timing statistics
        """
        # Reset stats for this batch
        self.stats.update({
            'total_time': 0.0,
            'image_load_time': 0.0,
            'inference_time': 0.0,
            'file_write_time': 0.0,
            'images_processed': 0,
            'images_failed': 0
        })
        
        start_total = time.perf_counter()
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Get all image files from input folder
        logger.info(f"Scanning for images in {input_folder}")
        image_files = [f for f in os.listdir(input_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            logger.warning(f"No image files found in {input_folder}")
            return self.stats
        
        logger.info(f"Found {len(image_files)} images to process")
        
        if parallel and len(image_files) > 1:
            # Process images in parallel
            logger.info(f"Processing images in parallel")
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Prepare arguments for each worker
                worker_args = [(image_file, input_folder, output_folder) for image_file in image_files]
                
                # Submit all tasks and track with progress bar if requested
                futures = list(executor.map(self._process_image_worker, worker_args))
                
                # Display progress if requested
                if show_progress:
                    for _ in tqdm(futures, total=len(worker_args), desc="Processing formulas"):
                        pass
        else:
            # Process each image sequentially with optional progress bar
            image_iter = tqdm(image_files, desc="Processing formulas") if show_progress else image_files
            for image_file in image_iter:
                image_path = os.path.join(input_folder, image_file)
                output_filename = os.path.splitext(image_file)[0] + '.tex'
                output_path = os.path.join(output_folder, output_filename)
                
                self.process_single_image(image_path, output_path)
        
        # Calculate total processing time
        self.stats['total_time'] = time.perf_counter() - start_total
        
        # Log summary statistics
        self._log_summary_statistics()
        
        return self.stats
    
    def _log_summary_statistics(self):
        """Log summary statistics of processing"""
        if self.stats['images_processed'] > 0:
            avg_time = (self.stats['image_load_time'] + self.stats['inference_time'] + self.stats['file_write_time']) / self.stats['images_processed']
            logger.info("\n=== Processing Summary ===")
            logger.info(f"Total processing time: {self.stats['total_time']:.3f} seconds")
            logger.info(f"Model initialization time: {self.stats['model_init_time']:.3f} seconds")
            logger.info(f"Total images processed: {self.stats['images_processed']}")
            logger.info(f"Failed images: {self.stats['images_failed']}")
            logger.info(f"Average time per image: {avg_time:.3f} seconds")
            logger.info(f"Average image load time: {self.stats['image_load_time'] / self.stats['images_processed']:.3f} seconds")
            logger.info(f"Average inference time: {self.stats['inference_time'] / self.stats['images_processed']:.3f} seconds")
            if self.stats['file_write_time'] > 0:
                logger.info(f"Average file write time: {self.stats['file_write_time'] / self.stats['images_processed']:.3f} seconds")
            logger.info(f"Performance: {self.stats['images_processed'] / self.stats['total_time']:.2f} images/second")
            
            # Calculate theoretical vs. actual speedup from parallelization
            if self.stats['total_time'] > 0 and self.stats['images_processed'] > 1:
                sequential_time = self.stats['image_load_time'] + self.stats['inference_time'] + self.stats['file_write_time']
                actual_time = self.stats['total_time']
                speedup = sequential_time / actual_time
                logger.info(f"Parallel processing speedup: {speedup:.2f}x")


def find_input_folder(base_paths):
    """Find the first existing folder from a list of possible paths"""
    for path in base_paths:
        if os.path.exists(path):
            return path
    return None

def process_formulas(input_folder: str, output_folder: str, show_progress: bool = True, 
                    parallel: bool = True, max_workers: Optional[int] = None, 
                    use_fast: bool = True) -> Dict[str, float]:
    """
    Process mathematical formulas from images and convert to LaTeX.
    
    This is a convenience function that creates a FormulaProcessor instance
    and processes a batch of images.
    
    Args:
        input_folder: Path to folder containing formula images
        output_folder: Path to save LaTeX output files
        show_progress: Whether to show a progress bar
        parallel: Whether to process images in parallel
        max_workers: Maximum number of parallel workers (None = auto)
        use_fast: Whether to use fast tokenization
        
    Returns:
        Dictionary containing timing statistics
    """
    processor = FormulaProcessor(use_fast=use_fast)
    return processor.process_batch(
        input_folder=input_folder, 
        output_folder=output_folder, 
        show_progress=show_progress,
        parallel=parallel,
        max_workers=max_workers
    )

def main():
    try:
        # Get absolute paths (makes paths more reliable)
        script_dir = Path(__file__).resolve().parent
        workspace_root = script_dir.parent
        
        # Configure input and output folders with proper path handling
        # Check for two possible locations of the images
        possible_input_paths = [
            # workspace_root / "Cropped_Elements" / "2501.00663v1" / "Formula",
            workspace_root / "Unstructured-Methods-1.0" / "Cropped_Elements" / "2501.00663v1" / "Formula",
            # workspace_root / "TEST RESULT 1.1" / "formulas"
        ]
        
        # Find the first valid input path
        input_folder = find_input_folder([str(path) for path in possible_input_paths])
        
        # Set output folder
        output_folder = workspace_root / "TEST RESULT 1.2" / "latex_output"
        
        logger.info(f"Starting formula processing...")
        
        if input_folder is None:
            logger.error("No valid input folder found! Tried:")
            for path in possible_input_paths:
                logger.error(f"  - {path}")
            logger.error("Please ensure one of these directories exists with formula images")
            return
            
        logger.info(f"Using input folder: {input_folder}")
        logger.info(f"Output folder: {output_folder}")
        
        # Check for images in the input folder
        image_count = len([f for f in os.listdir(input_folder) 
                        if str(f).lower().endswith(('.png', '.jpg', '.jpeg'))])
        logger.info(f"Found {image_count} images in input folder")
        
        if image_count == 0:
            logger.warning("No images found in the input folder!")
            return
        
        # Process formulas with overall timing and parallel processing
        start_total = time.perf_counter()
        stats = process_formulas(
            input_folder=str(input_folder), 
            output_folder=str(output_folder),
            parallel=True,  # Enable parallel processing
            use_fast=True   # Use fast tokenization
        )
        total_time = time.perf_counter() - start_total
        
        # Final performance summary
        success_rate = stats['images_processed'] / (stats['images_processed'] + stats['images_failed']) * 100 if stats['images_processed'] + stats['images_failed'] > 0 else 0
        logger.info(f"Processing complete. Success rate: {success_rate:.1f}%")
        logger.info(f"Total time including setup: {total_time:.3f} seconds")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()