from groq import Groq
import PyPDF2
import os
import json
from datetime import datetime
import logging

# Set up logging configuration
def setup_logging():
    """Configure logging with detailed format"""
    ensure_results_folder()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(f'results/{timestamp}_processing.log'),
            logging.StreamHandler()
        ]
    )

# Load environment variables manually
def load_env_variable(key):
    try:
        with open(".env", "r") as file:
            for line in file:
                if line.startswith(key + "="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        logging.error(".env file not found.")
    return None

# Get API key and set it in environment
API_KEY = load_env_variable("GROQ_API_KEY")
if API_KEY:
    os.environ["GROQ_API_KEY"] = API_KEY
else:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Initialize the Groq client
client = Groq(api_key=API_KEY)

def ensure_results_folder():
    """Create results folder if it doesn't exist."""
    if not os.path.exists("results"):
        os.makedirs("results")
        logging.info("Created results folder")

def save_output(content, filename):
    """Save content to a file in the results folder."""
    ensure_results_folder()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"results/{timestamp}_{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info(f"Saved output to: {filepath}")
    return filepath

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    logging.info(f"Starting PDF text extraction from: {pdf_path}")
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            logging.info(f"PDF has {total_pages} pages")
            
            for i, page in enumerate(pdf_reader.pages, 1):
                logging.info(f"Processing page {i}/{total_pages}")
                text += page.extract_text() + "\n"
    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
    return text

def chunk_text(text, max_chunk_size=2000):
    """Split text into smaller chunks."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_size += len(word) + 1
        if current_size > max_chunk_size:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    logging.info(f"Split text into {len(chunks)} chunks")
    return chunks

def extract_information_via_api(text):
    """Extracts information from text using Groq API."""
    try:
        chunks = chunk_text(text)
        extracted_info = []
        
        system_prompt = """
You are provided with raw text extracted from a PDF document. Your task is to produce a clear, concise summary of the content following these instructions:

1. Section-wise Organization:
   - Identify and respect the natural section divisions in the text.
   - Summarize each section in the order they appear in the document.
   - If the document has headings or sub-headings, use them as markers to structure your summary.

2. Markdown Formatting:
   - Format section headings as markdown headers (e.g., using '#', '##', etc.).
   - Use bullet points, numbered lists, or block quotes where appropriate to highlight key points.
   - Ensure the summary is easily navigable and readable with proper markdown syntax.

3. Content Requirements:
   - Capture the main ideas and critical details from each section.
   - Maintain the sequential flow of the document.
   - Be concise while preserving the essence of the original content.

4. Style and Clarity:
   - Write in clear, plain language.
   - Avoid unnecessary jargon unless it’s essential for understanding.
   - Ensure that the final summary is informative and well-organized.

Your final output should be a markdown-formatted summary that reflects the structure and main points of the original PDF text.
"""


        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            logging.info(f"Processing chunk {i}/{total_chunks} with llama-3.1-8b-instant")
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this text and provide a structured summary following the exact format specified: {chunk}"}
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )
            
            chunk_info = ""
            for response_chunk in completion:
                chunk_info += response_chunk.choices[0].delta.content or ""
            extracted_info.append(chunk_info)
            logging.info(f"Completed chunk {i} analysis")
            
        return "\n\n---\n\n".join(extracted_info)
    except Exception as e:
        logging.error(f"Error in llama API call: {e}")
        return ""

def batch_summaries(summaries, batch_size=3):
    """Batch summaries into smaller groups to avoid token limits."""
    return [summaries[i:i + batch_size] for i in range(0, len(summaries), batch_size)]

def summarize_text_with_groq(text):
    """Summarizes text using Groq."""
    try:
        if len(text) > 2000:
            chunks = chunk_text(text)
            summaries = []
            
            system_prompt = """
You are provided with multiple section summaries in markdown format. Your task is to produce a unified summary that not only lists the key points using bullet points but also includes a brief description for each section where applicable. Follow these instructions:

1. **Collect and Consolidate**:
   - Gather the individual section summaries provided.
   - Identify the key insights and common themes from each summary.
   - Detect distinct section headings (e.g., "Executive Summary", "Cybersecurity") and note their main focus.

2. **Unified Summary with Section-wise Descriptions**:
   - Create a concise unified summary using bullet points.
   - For each distinct section, include its title and a short description that captures its critical ideas.
   - Merge similar points where possible, but preserve unique insights tied to specific sections.

3. **Markdown Formatting**:
   - Format section titles as markdown sub-headers (e.g., using `###`).
   - Use markdown bullet point syntax (e.g., `-` or `*`) to list key points and descriptions.
   - Ensure the final output is fully formatted in markdown for clarity and readability.

4. **Clarity and Brevity**:
   - Keep the unified summary brief yet comprehensive.
   - Maintain clarity while ensuring all critical points and section details are represented.

Your final output should be a markdown-formatted unified summary that organizes key points and includes brief descriptions for each section.
"""


            total_chunks = len(chunks)
            for i, chunk in enumerate(chunks, 1):
                logging.info(f"Processing chunk {i}/{total_chunks} with gemma2-9b-it")
                completion = client.chat.completions.create(
                    model="gemma2-9b-it",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Create a detailed executive summary of this text following the exact format specified. Ensure all sections are completed with specific details: {chunk}"}
                    ],
                    temperature=0.7,
                    max_tokens=2048,
                    top_p=1,
                    stream=True,
                    stop=None
                )

                chunk_summary = ""
                for response_chunk in completion:
                    chunk_summary += response_chunk.choices[0].delta.content or ""
                summaries.append(chunk_summary)
                logging.info(f"Completed chunk {i} summary with length: {len(chunk_summary)}")
            
            if len(summaries) > 1:
                logging.info(f"Processing {len(summaries)} summaries in batches")
                # Process summaries in smaller batches
                batched_summaries = batch_summaries(summaries)
                intermediate_summaries = []
                
                for batch_idx, batch in enumerate(batched_summaries, 1):
                    logging.info(f"Processing summary batch {batch_idx}/{len(batched_summaries)}")
                    batch_text = " ".join(batch)
                    
                    completion = client.chat.completions.create(
                        model="gemma2-9b-it",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Create an executive summary combining these analyses. Focus on extracting and combining the most important points: {batch_text}"}
                        ],
                        temperature=0.7,
                        max_tokens=2048,
                        top_p=1,
                        stream=True,
                        stop=None
                    )
                    
                    batch_summary = ""
                    for chunk in completion:
                        batch_summary += chunk.choices[0].delta.content or ""
                    intermediate_summaries.append(batch_summary)
                    logging.info(f"Completed batch {batch_idx} summary with length: {len(batch_summary)}")
                
                # Final combination of intermediate summaries
                if len(intermediate_summaries) > 1:
                    logging.info("Creating final summary from intermediate summaries")
                    final_completion = client.chat.completions.create(
                        model="gemma2-9b-it",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Create a final comprehensive executive summary combining these analyses. Ensure all sections are complete and well-structured: {' '.join(intermediate_summaries[:3])}"}
                        ],
                        temperature=0.7,
                        max_tokens=2048,
                        top_p=1,
                        stream=True,
                        stop=None
                    )
                    
                    final_summary = ""
                    for chunk in final_completion:
                        final_summary += chunk.choices[0].delta.content or ""
                    logging.info(f"Generated final summary with length: {len(final_summary)}")
                    return final_summary
                else:
                    logging.info(f"Returning single intermediate summary with length: {len(intermediate_summaries[0])}")
                    return intermediate_summaries[0]
            
            logging.info(f"Returning single chunk summary with length: {len(summaries[0])}")
            return summaries[0]
        else:
            logging.info("Processing single chunk with gemma2-9b-it")
            completion = client.chat.completions.create(
                model="gemma2-9b-it",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a detailed executive summary of this text following the exact format specified. Ensure all sections are completed with specific details: {text}"}
                ],
                temperature=0.7,
                max_tokens=2048,
                top_p=1,
                stream=True,
                stop=None
            )

            summary = ""
            for chunk in completion:
                summary += chunk.choices[0].delta.content or ""
            logging.info(f"Generated direct summary with length: {len(summary)}")
            return summary
    except Exception as e:
        logging.error(f"Error in gemma API call: {e}")
        if isinstance(e, str) and "413" in e:
            logging.warning("Received 413 error, attempting to process with smaller batch")
            # Add fallback processing here if needed
        return ""

# Main function
if __name__ == "__main__":
    setup_logging()
    logging.info("Starting PDF processing pipeline")
    
    pdf_path = "input/4.pdf"
    logging.info(f"Processing PDF: {pdf_path}")

    # Step 1: Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    if pdf_text:
        # Save extracted text
        extracted_text_file = save_output(pdf_text, "extracted_text.txt")
        logging.info(f"Saved extracted text ({len(pdf_text)} characters)")

        # Step 2: Extract information via API (llama-3.1-8b-instant)
        logging.info("Starting structured analysis with llama-3.1-8b-instant")
        extracted_info = extract_information_via_api(pdf_text)
        structured_analysis_file = save_output(extracted_info, "structured_analysis.md")
        logging.info("Completed structured analysis")

        # Step 3: Summarize extracted information (gemma2-9b-it)
        logging.info("Starting final summary with gemma2-9b-it")
        summary = summarize_text_with_groq(extracted_info)
        final_summary_file = save_output(summary, "final_summary.md")
        logging.info("Completed final summary")

        # Print the results
        print("\nProcessing completed successfully!")
        print(f"\nFiles generated:")
        print(f"1. Extracted text: {extracted_text_file}")
        print(f"2. Structured analysis: {structured_analysis_file}")
        print(f"3. Final summary: {final_summary_file}")
        
        logging.info("Processing pipeline completed successfully")
    else:
        logging.error("Failed to extract text from the PDF")
        print("Failed to extract text from the PDF.")