import streamlit as st
import os
from fp import (create_directory, write_file_tool, compile_links_for_company,
                scrape_and_store_links_pdfs, classify_docs, note_taking,
                create_sectioned_notes, create_report, convert_html_to_docx)

def update_directory_view(directory_path):
    files = []
    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            files.append(os.path.join(root, filename).replace(directory_path + '/', ''))
    return files

def generate_save_ddreport(company_name: str, num_links: int = 2):
    st.write("Creating directory....")
    directory_creation_response = create_directory(company_name)
    st.write(directory_creation_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Creating links.txt file....")
    links_file_creation_response = write_file_tool(company_name, "links.txt", "")
    st.write(links_file_creation_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Compiling links for the company....")
    compile_links_response = compile_links_for_company(company_name, num_links)
    st.write(compile_links_response)
    st.write("Links added to links.txt file....")
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Scraping and storing links and PDFs....")
    scraping_response = scrape_and_store_links_pdfs(company_name, "links.txt")
    st.write(scraping_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Classifying documents....")
    classification_response = classify_docs(company_name)
    st.write(classification_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Taking notes....")
    note_taking_response = note_taking(company_name, "notes.txt")
    st.write(note_taking_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Sectioning notes...")
    notes_sectioned_response = create_sectioned_notes(company_name, "notes.txt")
    st.write(notes_sectioned_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Creating report....")
    report_creation_response = create_report(company_name, "sectioned_notes.txt")
    st.write(report_creation_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Converting report to DOCX....")
    conversion_response = convert_html_to_docx(company_name, os.path.join(company_name, "due_diligence_report.html"))
    st.write(conversion_response)
    st.session_state['files'] = update_directory_view(company_name)

    st.write("Due diligence report generation and saving process completed.")
    
    # Provide download button for the DOCX file
    docx_file_path = os.path.join(company_name, "due_diligence_report-converted.docx")
    if os.path.exists(docx_file_path):
        with open(docx_file_path, "rb") as file:
            st.download_button(label="Download Due Diligence Report",
                               data=file,
                               file_name="due_diligence_report-converted.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# Streamlit App
st.title('Due Diligence Report Generator')

company_name = st.text_input("Enter company name:")

if 'files' not in st.session_state:
    st.session_state['files'] = []

if company_name:
    col1, col2 = st.columns(2)

    with col1:
        st.header("Company Directory")
        directory_path = os.path.join(os.getcwd(), company_name)
        dir_placeholder = st.empty()
        
        with dir_placeholder.container():
            st.write(f"Files in {company_name} directory:")
            for file in st.session_state['files']:
                st.write(file)
        
    with col2:
        st.header("Process Log")
        process_log_placeholder = st.empty()
        
        if st.button("Generate Due Diligence Report", key="generate_report_button"):
            with process_log_placeholder:
                st.write(f"Processing for {company_name}...")

            # Run the generation process
            generate_save_ddreport(company_name)

            # Update the directory view
            st.session_state['files'] = update_directory_view(directory_path)
            with dir_placeholder.container():
                st.write(f"Files in {company_name} directory:")
                for file in st.session_state['files']:
                    st.write(file)

    # Initial directory check after rendering the layout
    if os.path.exists(directory_path):
        st.session_state['files'] = update_directory_view(directory_path)
        with dir_placeholder.container():
            st.write(f"Files in {company_name} directory:")
            for file in st.session_state['files']:
                st.write(file)
    else:
        st.write(f"Directory for {company_name} does not exist.")