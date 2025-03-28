import streamlit as st
import tempfile
import os
import base64
from Update import DocuMindO
from pathlib import Path

# Set page configuration at the very beginning
st.set_page_config(
    page_title="DocuMind-O",
    page_icon="🔍",
    layout="wide"
)

class DocuMindApp:
    """Main application class for DocuMind"""
    
    def __init__(self):
        """Initialize the application"""
        try:
            self.assets_dir = Path(__file__).parent / "assets"
            self.logo_path = str(self.assets_dir / "PVlogo-1024x780.webp")
            self.initialize_session_state()
            self.documind = self.load_model()
            
            # Add custom CSS without st.set_page_config
            st.markdown("""
            <style>
            /* Add your custom styles here */
            </style>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error initializing application: {str(e)}")
            raise

    @staticmethod
    def initialize_session_state():
        """Initialize Streamlit session state variables"""
        session_vars = {
            "extracted_text": "",
            "last_uploaded_image": None,
            "new_output": ""
        }
        for var, default in session_vars.items():
            if var not in st.session_state:
                st.session_state[var] = default

    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_model():
        """Load and cache the DocuMind model"""
        try:
            with st.spinner("Loading models..."):
                return DocuMindO()
        except Exception as e:
            st.error(f"Failed to load models: {str(e)}")
            raise

    def render_header(self):
        """Render the application header"""
        col1, col2 = st.columns([1, 8])
        with col1:
            st.image(self.logo_path, width=220)
        with col2:
            st.title("DocuMind-o")
            st.subheader("AI-Powered Document Processing System")

    def process_file(self, uploaded_file, doc_type, user_prompt=None):
        """Process uploaded file with error handling"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
                
            result = self.documind.process_image(temp_path, doc_type=doc_type, user_prompt=user_prompt)
            return result
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
        finally:
            if 'temp_path' in locals():
                os.unlink(temp_path)

    def display_image_preview(self, uploaded_file):
        """Display preview of uploaded image"""
        image_data = uploaded_file.getvalue()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        st.markdown(f"""
        <div style="position: relative;">
            <img src="data:image/png;base64,{base64_image}" style="width: 100%; border-radius: 15px;">
        </div>
        """, unsafe_allow_html=True)

    def handle_text_extraction(self, uploaded_file, doc_type):
        """Handle the text extraction process"""
        if st.button("Extract Text", type="primary", key="extract_btn", use_container_width=True):
            st.session_state.extracted_text = ""
            with st.spinner("Processing document..."):
                result = self.process_file(uploaded_file, doc_type)
                if result['status'] == 'success':
                    st.session_state.extracted_text = result['original_text']
                    return True
                else:
                    st.error(result['message'])
                    return False
        
        if st.session_state.extracted_text:
            st.download_button(
                "Download Original Text",
                data=st.session_state.extracted_text,
                file_name="original_text.txt",
                mime="text/plain",
                key="download_original",
                use_container_width=True
            )

    def handle_text_refinement(self, uploaded_file, doc_type):
        """Handle text refinement with user input"""
        if st.session_state.extracted_text:
            # Display original text
            st.text_area(
                "Extracted Text", 
                value=st.session_state.extracted_text, 
                height=150,
                key="original_text"
            )
            
            # User input section
            st.subheader("Text Refinement")
            user_input = st.text_area(
                "Enter specific instructions for refinement:",
                "",
                help="Examples:\n- Focus on dates and numbers\n- Ignore signatures\n- Extract only addresses",
                key="user_input",
                height=80
            )
            
            # Refinement button and processing
            if st.button("Process with Instructions", type="primary", key="refine_btn", use_container_width=True):
                if user_input.strip():
                    with st.spinner("Processing with your instructions..."):
                        refined_result = self.process_file(
                            uploaded_file, 
                            doc_type, 
                            user_input.strip()
                        )
                        
                        if refined_result['status'] == 'success':
                            st.session_state.new_output = refined_result['modified_text']
                            
                            # Display refined text
                            st.text_area(
                                "Refined Text",
                                value=refined_result['modified_text'],
                                height=150,
                                key="refined_text"
                            )
                            
                            # Download buttons in two columns
                            dl_col1, dl_col2 = st.columns(2)
                            with dl_col1:
                                st.download_button(
                                    "Download Original",
                                    data=st.session_state.extracted_text,
                                    file_name="original_text.txt",
                                    mime="text/plain",
                                    key="download_original_refined",
                                    use_container_width=True
                                )
                            with dl_col2:
                                st.download_button(
                                    "Download Refined",
                                    data=refined_result['modified_text'],
                                    file_name="refined_text.txt",
                                    mime="text/plain",
                                    key="download_refined",
                                    use_container_width=True
                                )
                        else:
                            st.error(refined_result['message'])
                else:
                    st.warning("Please enter instructions for refinement")

    def handle_image_processing(self):
        """Handle image processing tab"""
        st.write("### Image Processing")
        doc_type = st.radio("Select document type:", ("Typed", "Handwritten"), horizontal=True)
        uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            st.session_state.last_uploaded_image = uploaded_file
            
            # Create two columns for layout
            preview_col, process_col = st.columns([1, 1])
            
            # Left column: Image Preview
            with preview_col:
                st.subheader("Document Preview")
                self.display_image_preview(uploaded_file)
            
            # Right column: Text Processing
            with process_col:
                st.subheader("Text Extraction")
                # Handle text extraction
                self.handle_text_extraction(uploaded_file, doc_type)
                
                # Handle refinement if text was extracted
                if st.session_state.extracted_text:
                    st.markdown("---")  # Add separator
                    self.handle_text_refinement(uploaded_file, doc_type)

        # Add some styling to make the columns look better
        st.markdown("""
            <style>
            .stImage > img {
                border-radius: 10px;
                border: 1px solid #ddd;
            }
            .stTextArea > div > textarea {
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_footer():
        """Render the application footer"""
        st.markdown("""
        <div style='text-align: center'>
            <p>Powered by DocuMind-o.1 | Powered by Software Team @ProcessVenue | AI Document Processing System</p>
            <p>Copyright © 2025 ProcessVenue. All rights reserved.</p>
            <p>Version 1.0.1</p>
            <p>Contact us for queries at <a href='mailto:it.ops@predusk.com'>it.ops@predusk.com</a></p>
        </div>
        """, unsafe_allow_html=True)

    def run(self):
        """Run the application"""
        try:
            self.render_header()
            self.handle_image_processing()
            self.render_footer()
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def main():
    app = DocuMindApp()
    app.run()

if __name__ == "__main__":
    main()

