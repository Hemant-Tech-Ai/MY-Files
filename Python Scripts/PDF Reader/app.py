from PyPDF2 import PdfReader

# Function to load a PDF file and extract its text
def load_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return None


# Example usage
if __name__ == "__main__":
    pdf_path = "input/5.pdf"  # Replace with the path to your PDF
    extracted_info = load_pdf(pdf_path)

    if extracted_info:
        print(extracted_info)