import base64
import requests
import os
import logging
import google.generativeai as genai
import pandas as pd
from pathlib import Path
from PIL import Image
import io
import warnings

# Suppress gRPC warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Configure Gemini before any operations
os.environ['GRPC_PYTHON_LOG_LEVEL'] = '2'  # Suppress gRPC logs
genai.configure(api_key="AIzaSyAvXqNJbC79DQu2TPPTKEMqZLrc95p8hF4")

# Set up logging to a different filep
log_file = "ocr_process.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

console_logger = logging.getLogger("console")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
console_logger.addHandler(console_handler)

# Create output directory if it doesn't exist
OUTPUT_DIR = Path("markdown_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def initialize_model(model_name="gemini-1.5-flash-8b"):
    """Initialize the Gemini model with configuration"""
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )

def process_images_folder(input_folder="images"):
    """Process all images in the input folder and save results to markdown files."""
    input_path = Path(input_folder)
    
    if not input_path.exists():
        console_logger.error(f"Input folder {input_folder} does not exist!")
        return
    
    # Process each image file
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    for image_file in input_path.glob('*'):
        if image_file.suffix.lower() in image_extensions:
            console_logger.info(f"Processing {image_file.name}")
            
            # Generate markdown content
            markdown_content = ocr(str(image_file))
            
            # Create output filename
            output_file = OUTPUT_DIR / f"{image_file.stem}.md"
            
            # Save markdown content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            console_logger.info(f"Saved markdown to {output_file}")
            
            # Calculate and log cost
            cost = calculate_cost(str(image_file))
            if cost is not None:
                console_logger.info(f"Cost for {image_file.name}: ${cost:.4f}")

def ocr(file_path, api_key=None, model="gemini-1.5-flash-8b"):
    console_logger.info("Code started")
    logging.info(f"Starting OCR process for file: {file_path}")

    model_instance = initialize_model(model)
    final_markdown = get_markdown(model_instance, file_path)

    logging.info("OCR process completed successfully")
    console_logger.info("Code completed")
    return final_markdown

def get_markdown(model_instance, file_path):
    logging.info("Starting Markdown generation from image")
    system_prompt = (
        "Extract the following key information from the check image and format it in Markdown:\n\n"
        
        "## Check Details\n"
        "- **Payee Name**: [Full name of who the check is written to]\n"
        "- **Payer Name**: [Full name of who wrote/signed the check]\n"
        "- **Bank Name**: [Name of the bank]\n"
        "- **Amount**: [Numerical amount on check]\n"
        "- **Check Date**: [Date written on check]\n"
        "- **Check Number**: [Check number if visible]\n\n"
        
        "Requirements:\n"
        "1. Be precise with names and amounts\n"
        "2. If any field is not visible or unclear, mark it as 'Not visible'\n"
        "3. If multiple payees or payers exist, list all names\n"
        "4. Format amount in both numerical ($XX.XX) and written forms\n"
    )

    try:
        if is_remote_file(file_path):
            logging.info("File is a remote URL")
            image_data = requests.get(file_path).content
            image = Image.open(io.BytesIO(image_data))
        else:
            logging.info("File is a local path, reading image")
            image = Image.open(file_path)

        chat = model_instance.start_chat(history=[])
        
        response = chat.send_message([
            system_prompt,
            image  # Pass the PIL Image directly
        ])
        logging.info("Received response from Gemini API")
        return response.text
    except Exception as e:
        logging.error(f"Error processing image with Gemini: {e}")
        return f"Error: Unable to process the image: {str(e)}"

def encode_image(image_path):
    logging.info(f"Encoding image from path: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def is_remote_file(file_path):
    logging.info(f"Checking if file is remote: {file_path}")
    return file_path.startswith("http://") or file_path.startswith("https://")

def calculate_cost(image_path):
    logging.info(f"Calculating cost for image: {image_path}")
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            tokens = min(2, max(height // 560, 1)) * min(2, max(width // 560, 1)) * 1601
            cost = tokens * 0.0001  # Assuming cost per token is $0.0001
            logging.info(f"Image dimensions: Width={width}, Height={height}, Tokens={tokens}, Cost=${cost:.4f}")
            return cost
    except Exception as e:
        logging.error(f"Error calculating cost: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    try:
        process_images_folder()
    except Exception as e:
        logging.error(f"Main process error: {str(e)}")
        console_logger.error(f"Error: {str(e)}")