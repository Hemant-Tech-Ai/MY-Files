# from groq import Groq
# import PyPDF2
# import os

# # Load environment variables manually
# def load_env_variable(key):
#     try:
#         with open(".env", "r") as file:
#             for line in file:
#                 if line.startswith(key + "="):
#                     return line.strip().split("=", 1)[1]
#     except FileNotFoundError:
#         print(".env file not found.")
#     return None

# API_KEY = load_env_variable("API_KEY")

# # Initialize the Groq client
# client = Groq()

# def extract_text_from_pdf(pdf_path):
#     """Extracts text from a PDF file."""
#     text = ""
#     try:
#         with open(pdf_path, 'rb') as pdf_file:
#             pdf_reader = PyPDF2.PdfReader(pdf_file)
#             for page in pdf_reader.pages:
#                 text += page.extract_text() + "\n"
#     except Exception as e:
#         print(f"Error reading PDF: {e}")
#     return text

# def extract_information_with_groq_client(text):
#     """Extracts information from text using the Groq client."""
#     try:
#         completion = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant for extracting key information from documents."},
#                 {"role": "user", "content": text}
#             ],
#             temperature=1,
#             max_tokens=1024,
#             top_p=1,
#             stream=False,
#             stop=None
#         )
#         return completion.choices[0].message
#     except Exception as e:
#         print(f"Error making API call with Groq client: {e}")
#         return None

# def summarize_text_with_groq_client(text):
#     """Summarizes text using the Groq client."""
#     try:
#         completion = client.chat.completions.create(
#             model="gemma2-9b-it",
#             messages=[
#                 {"role": "system", "content": "You are a summarization assistant."},
#                 {"role": "user", "content": f"Summarize the following text: {text}"}
#             ],
#             temperature=1,
#             max_tokens=1024,
#             top_p=1,
#             stream=True,
#             stop=None
#         )

#         summary = ""
#         for chunk in completion:
#             summary += chunk.choices[0].delta.content or ""

#         # Ensure output is formatted as a readable paragraph
#         return " ".join(summary.splitlines()).strip()
#     except Exception as e:
#         print(f"Error summarizing text with Groq client: {e}")
#         return ""

# # Main function
# if __name__ == "__main__":
#     pdf_path = "5.pdf"  # Replace with your PDF file path

#     # Step 1: Extract text from the PDF
#     pdf_text = extract_text_from_pdf(pdf_path)

#     if pdf_text:
#         print("Extracted Text from PDF:\n", pdf_text)  # Displaying all extracted text

#         # Step 2: Extract information with Groq client
#         extracted_info = extract_information_with_groq_client(pdf_text)
#         print("\nExtracted Information:\n", extracted_info)

#         # Step 3: Summarize extracted information
#         summary = summarize_text_with_groq_client(extracted_info)
#         print("\nSummary:\n", summary)
#     else:
#         print("Failed to extract text from the PDF.")

#--------------------------------------------------
from groq import Groq
import PyPDF2
import os

# Load environment variables manually
def load_env_variable(key):
    try:
        with open(".env", "r") as file:
            for line in file:
                if line.startswith(key + "="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        print(".env file not found.")
    return None

API_KEY = load_env_variable("API_KEY")


# Initialize the Groq client
client = Groq()

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_information_with_groq_client(text, prompt):
    """Extracts information from text using the Groq client."""
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an assistant tasked with extracting the most critical and concise information from the following text. Focus on key points, main ideas, and insights, avoiding unnecessary details."},
                {"role": "user", "content": prompt + text}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        return completion.choices[0].message
    except Exception as e:
        print(f"Error making API call with Groq client: {e}")
        return None

def summarize_text_with_groq_client(text):
    """Summarizes text using the Groq client."""
    try:
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": "You are a summarization assistant."},
                {"role": "user", "content": f"Summarize the following text: {text}"}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        summary = ""
        for chunk in completion:
            summary += chunk.choices[0].delta.content or ""

        # Ensure output is formatted as a readable paragraph
        return " ".join(summary.splitlines()).strip()
    except Exception as e:
        print(f"Error summarizing text with Groq client: {e}")
        return ""

def format_extracted_information(raw_content):
    """Formats the raw extracted information into a cleaner structure."""
    formatted_content = raw_content.replace("**", "").replace("\n\n", "\n").strip()
    formatted_lines = formatted_content.split("\n")
    
    formatted_output = ""
    for line in formatted_lines:
        if line.startswith("Key Points:"):
            formatted_output += "\nKey Points\n"
        elif line.startswith("Insights:"):
            formatted_output += "\nInsights\n"
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5."):
            formatted_output += f" - {line[3:].strip()}\n"
        else:
            formatted_output += f"{line}\n"
    
    return formatted_output

# Main function
if __name__ == "__main__":
    input_folder = "input"  # Folder containing the PDF files
    output_folder_extracted = "output_extracted"  # Folder for extracted information
    output_folder_summary = "output_summary"  # Folder for summarized information

    # Create output directories if they don't exist
    os.makedirs(output_folder_extracted, exist_ok=True)
    os.makedirs(output_folder_summary, exist_ok=True)

    # Iterate over PDF files in the input folder
    for pdf_file in os.listdir(input_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, pdf_file)
            print(f"Processing file: {pdf_file}")

            # Step 1: Extract text from the PDF
            pdf_text = extract_text_from_pdf(pdf_path)

            if pdf_text:
                # Step 2: Customize prompt for extracting information
                prompt = "Please extract the key points and insights from the following text:\n"
                extracted_info = extract_information_with_groq_client(pdf_text, prompt)

                # Format and save the extracted information
                if extracted_info:
                    formatted_info = format_extracted_information(extracted_info.content)
                    extracted_output_path = os.path.join(output_folder_extracted, f"{os.path.splitext(pdf_file)[0]}_extracted.txt")
                    with open(extracted_output_path, "w", encoding="utf-8") as f:
                        f.write(formatted_info)

                # Step 3: Summarize extracted information
                summary = summarize_text_with_groq_client(extracted_info.content)
                if summary:
                    summary_output_path = os.path.join(output_folder_summary, f"{os.path.splitext(pdf_file)[0]}_summary.txt")
                    with open(summary_output_path, "w", encoding="utf-8") as f:
                        f.write(summary)

                print(f"Processed and saved outputs for: {pdf_file}")
            else:
                print(f"Failed to extract text from: {pdf_file}")

