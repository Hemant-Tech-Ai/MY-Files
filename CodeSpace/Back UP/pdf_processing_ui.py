#### CSV DATA Frame is used to display the table in the UI

import streamlit as st
import tempfile
import os
from pathlib import Path
import pandas as pd
import time

def pdf_processing_tab(documind):
    """Handle PDF processing UI and logic"""
    st.write("### PDF Processing")
    st.write("Upload a PDF file to extract text, tables, and images")
    
    # File uploader in full width
    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=['pdf'],
        key="pdf_uploader"
    )

    # Create columns for process button and timer below uploader
    button_col, timer_col = st.columns([1, 2])
    
    with button_col:
        # Custom CSS to increase button height
        st.markdown("""
            <style>
            .stButton button {
                height: 4rem;
            }
            </style>
            """, unsafe_allow_html=True)
        process_pdf_btn = st.button(
            "Process PDF", 
            type="primary",
            disabled=not uploaded_pdf
        )
    
    # Timer placeholder in the second column
    timer_placeholder = timer_col.empty()
        
    if uploaded_pdf and process_pdf_btn:
        start_time = time.time()
        with st.spinner("Processing your PDF..."):
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_pdf.getvalue())
                    temp_path = tmp_file.name

                # Process PDF
                results = documind.process_pdf(temp_path)
                
                # Calculate processing time
                end_time = time.time()
                processing_time = end_time - start_time
                timer_placeholder.info(f"Processing Time: {processing_time:.2f} seconds")
                
                # Create tabs for different types of content
                content_tabs = st.tabs(["Images", "Tables", "Text"])
                
                with content_tabs[0]:
                    show_images(results)
                
                with content_tabs[1]:
                    show_tables(results)
                
                with content_tabs[2]:
                    show_text_content(results)
                    
                
                # Download all content
                with open(results['zip_path'], 'rb') as f:
                    st.download_button(
                        label="Download All Extracted Content",
                        data=f,
                        file_name=f"{Path(uploaded_pdf.name).stem}_extracted.zip",
                        mime="application/zip",
                        type="primary"
                    )

                # Clean up
                os.unlink(temp_path)

            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                timer_placeholder.error(f"Processing failed after {processing_time:.2f} seconds")
                st.error(f"An error occurred: {str(e)}")

def show_tables(results):
    """Display extracted tables from PDF"""
    st.subheader("Extracted Tables")
    
    table_paths = results.get('tables')
    if not table_paths:
        st.info("No tables found in the document")
        return
        
    # Group tables by page number
    tables_by_page = {}
    for table_path in table_paths:
        # Extract page number from filename (page_1_table_1.csv)
        page_num = int(Path(table_path).stem.split('_')[1])
        
        if page_num not in tables_by_page:
            tables_by_page[page_num] = []
        tables_by_page[page_num].append(table_path)
    
    # Display tables page by page
    for page_num in sorted(tables_by_page.keys()):
        st.markdown(f"#### Page {page_num}")
        
        # Show tables for this page
        for table_path in sorted(tables_by_page[page_num]):
            try:
                df = pd.read_csv(table_path)
                table_num = int(Path(table_path).stem.split('_')[3])
                
                with st.expander(f"Table {table_num}", expanded=True):
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Add download button for each table
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"page_{page_num}_table_{table_num}.csv",
                        mime="text/csv",
                        key=f"download_table_{page_num}_{table_num}"
                    )
            except Exception as e:
                st.error(f"Error loading table from {table_path}: {str(e)}")
        
        st.markdown("---")

def show_images(results):
    """Display extracted images in a grid"""
    st.subheader("Extracted Images")
    
    if not results.get('images'):
        st.info("No images found in the document")
        return
    
    # Group images by page
    images_by_page = {}
    for img_path in results['images']:
        page_num = int(Path(img_path).stem.split('_')[1])
        if page_num not in images_by_page:
            images_by_page[page_num] = []
        images_by_page[page_num].append(img_path)
    
    # Display images page by page
    for page_num in sorted(images_by_page.keys()):
        st.markdown(f"#### Page {page_num} Images")
        cols = st.columns(4)  # 4 columns for thumbnails
        for idx, img_path in enumerate(images_by_page[page_num]):
            with cols[idx % 4]:
                # Create an expander for each image
                with st.expander(f"Image {idx + 1}", expanded=True):
                    # Display image with full width inside expander
                    st.image(img_path, use_container_width=True)
                    
                    # Add download button for each image
                    with open(img_path, 'rb') as img_file:
                        st.download_button(
                            label="Download Image",
                            data=img_file,
                            file_name=Path(img_path).name,
                            mime="image/png",
                            key=f"download_image_{page_num}_{idx}"
                        )
        st.markdown("---")

def show_text_content(results):
    """Display extracted text content from PDF"""
    st.subheader("Extracted Text")
    
    text_paths = results.get('texts')
    if not text_paths:
        st.info("No text content extracted from the document")
        return
    
    # Group text files by page number
    texts_by_page = {}
    for text_path in text_paths:
        # Extract page number from filename (page_1.txt)
        filename = os.path.basename(text_path)
        page_num = int(filename.split('_')[1].split('.')[0])
        texts_by_page[page_num] = text_path
    
    # Display text content page by page
    for page_num in sorted(texts_by_page.keys()):
        st.markdown(f"#### Page {page_num}")
        
        # Look for debug image for this page
        debug_image_path = next(
            (path for path in results.get('debug_images', [])
             if f'page_{page_num}_text_debug.png' in path),
            None
        )
        
        # Show debug image if available
        if debug_image_path and os.path.exists(debug_image_path):
            st.image(
                debug_image_path,
                caption=f"Text Detection - Page {page_num}",
                use_column_width=True
            )
        
        # Show text content
        try:
            with open(texts_by_page[page_num], 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            with st.expander("Content", expanded=True):
                st.text_area(
                    label="Content",
                    value=text_content,
                    height=300,
                    key=f"text_content_{page_num}"
                )
                
                # Add download button for text content
                st.download_button(
                    label="Download Text",
                    data=text_content.encode('utf-8'),
                    file_name=f"page_{page_num}_text.txt",
                    mime="text/plain",
                    key=f"download_text_{page_num}"
                )
        except Exception as e:
            st.error(f"Error loading text from page {page_num}: {str(e)}")
        
        st.markdown("---")

def show_debug_images(results):
    """Display debug images from PDF processing"""
    st.subheader("Debug Images")
    
    if not results.get('debug_images'):
        st.info("No debug images found in the document")
        return
    
    # Display debug images
    for img_path in results['debug_images']:
        st.image(img_path, caption=f"Debug Image: {os.path.basename(img_path)}", use_column_width=True)