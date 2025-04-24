import os
import fnmatch
import time
import streamlit as st
from pathlib import Path
import tempfile
from langchain_google_genai import GoogleGenerativeAI
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()
# Set up environment variable for Google API key
os.getenv('GOOGLE_API_KEY')

# Initialize the LLM model
model = GoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.2,
)   

def frontend_files(project_path):
    frontend_data = []
    
    # Walk through the project directory to read the frontend files
    for root, dirs, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)

            if fnmatch.fnmatch(file, '*.html') or fnmatch.fnmatch(file, '*.css') or fnmatch.fnmatch(file, '*.js') or fnmatch.fnmatch(file, '*.jsx'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    frontend_data.append(f"---\nFile: {file}\nContent:\n{content}\n")
    return frontend_data

def backend_files(project_path):
    backend_data = []
    
    # Walk through the project directory to read the backend files
    for root, dirs, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)

            if fnmatch.fnmatch(file, '*.py') or fnmatch.fnmatch(file, '*.java') or fnmatch.fnmatch(file, '*.php') or fnmatch.fnmatch(file, '*.NET'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    backend_data.append(f"---\nFile: {file}\nContent:\n{content}\n")
    return backend_data

def generate_pdf(final_response):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Project Workflow Documentation", ln=True, align='C')
    pdf.ln(10)  # Line break

    pdf.multi_cell(0, 10, txt=f"Final Response:\n{final_response}")

    # Save the PDF to a file
    pdf_output = "project_workflow_documentation.pdf"
    pdf.output(pdf_output)

    return pdf_output

def process_project(project_path):
    if not os.path.isdir(project_path):
        st.error('The provided path is not a valid directory.')
        return
    
    # Call the read_project_files function with the provided path
    front_data = frontend_files(project_path)
    back_data = backend_files(project_path)
    
    # Define the prompt templates
    front_template = f"""You are an AI documentation assistant tasked with generating project workflow documentation based on the provided frontend code. 
    Your goal is to analyze the contents of the specified project folder and create a clear, step-by-step workflow documentation using given data{front_data}.
    Instructions:
    * Read all files present in the specified project folder.
    * Generate a detailed project workflow documentation that outlines the structure, components, and flow of the frontend code.  
    """

    back_template = f"""
    You are an AI documentation assistant responsible for analyzing backend code and providing comprehensive documentation on its functionality and workflow. 
    Your analysis should focus on the route APIs present in the project and any additional relevant components.
    Generate using the given data {back_data}.
    Instructions:
    * Examine the backend code in the specified project folder.
    * Identify and document the functionality of each route API.
    * Provide a clear workflow that illustrates how the APIs interact and any other important elements in the codebase.
    """

    # Request the responses
    time.sleep(60)
    front_response = model.invoke(front_template)
    # st.write(front_response)
    time.sleep(60)
    back_response = model.invoke(back_template)
    # st.write(back_response)

    final_template = f"""You are an AI documentation assistant tasked with generating final workflow documentation for a project. 
    This documentation should integrate the insights from both the frontend and backend data provided.
    Instructions:
    * Review the documentation generated from the frontend data: {front_response}.
    * Review the documentation generated from the backend data: {back_response}.    
    * Create a cohesive, step-by-step workflow documentation that combines both frontend and backend insights for easy understanding by the user.
    * Include separate workflows for any user type validations or specific functionality based on user roles.
    * Ensure the final documentation is written in a clear and structured manner so that the user can easily understand the project workflow.
    * Also provide the details or points referring to the generated document so that the user can present about the project.
    """

    time.sleep(90)
    final_response = model.invoke(final_template)
    st.write(final_response)

    # Generate PDF
    pdf_file = generate_pdf(final_response)

    # Provide a download link
    with open(pdf_file, "rb") as f:
        st.download_button (
            label="Download PDF",
            data=f,
            file_name=pdf_file,
            mime="application/pdf"
        )
def save_uploaded_folder(uploaded_files):
    """Recreate the uploaded folder structure in a temp directory."""
    temp_dir = tempfile.mkdtemp()
    for uploaded_file in uploaded_files:
        file_path = Path(uploaded_file.name)  # Preserves relative path if uploaded from folder
        save_path = Path(temp_dir) / file_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
    return temp_dir

def main():
    st.title("Project Workflow Document Generator")
    # Text input for the project path
    project_path = st.text_input("Enter the project folder path:")

    if project_path:
        process_project(project_path)
    st.write("<center>(OR)</center>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload folder(select all files inside it):", accept_multiple_files=True)

    if uploaded_files:
        project_path = save_uploaded_folder(uploaded_files)
        st.info(f"Folder uploaded and saved to temporary path: {project_path}")
        process_project(project_path)

if __name__ == "__main__":
    main()




