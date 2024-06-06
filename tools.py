
from langchain.tools import tool
import os

import os
import requests
from langchain.agents import load_tools
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.utilities import BingSearchAPIWrapper
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from pydantic import BaseModel, Field
from typing import Type
import os
from pydantic import BaseModel, Field
from typing import Type
from langchain.tools import BaseTool


load_dotenv()
bing_subscription_key = os.getenv("BING_SUBSCRIPTION_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
os.environ["BING_SEARCH_URL"] = "https://api.bing.microsoft.com/v7.0/search"

OpenAIGPT4O = ChatOpenAI(
    model="gpt-4o"
)
agent_finishes  = []

def scrape_website(objective: str, url: str) -> str:
    print("Starting Scraping....")

    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = ChromeService() 
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    time.sleep(5) 

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")
    text = soup.get_text()
    # print("CONTENT:", text)

    return text

def summary(objective: str, content: str) -> str:
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")
    print("Creating summary....")

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([content])
    map_prompt = """
    Write a summary of the following text for {objective}:
    "{text}"
    SUMMARY:
    """
    map_prompt_template = PromptTemplate(
        template=map_prompt, input_variables=["text", "objective"])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True
    )

    output = summary_chain.run(input_documents=docs, objective=objective)

    return output

# --------------------------------------------------------------------Defining tools 

# RESULTS_PER_QUESTION = 3

search = BingSearchAPIWrapper()

@tool("Web_Search")
def web_search(question: str, links_per_query: int) -> str:
    """Performs a web search and returns a list of links to the top results."""
    results = search.results(question, links_per_query)
    return [r["link"] for r in results]


@tool("Scrape Website")
def scrape_website_tool(objective: str, url: str) -> str:
    """Scrapes a website and optionally summarizes its content based on the given objective."""
    return scrape_website(objective, url)

@tool("Create Directory")
def create_directory(directory_name: str) -> str:
    """Creates a directory with the given name in the project folder."""
    project_path = os.path.dirname(os.path.abspath(__file__))  # Assuming this script is in the project folder
    new_directory_path = os.path.join(project_path, directory_name)
    try:
        os.makedirs(new_directory_path, exist_ok=True)
        return f"Directory '{directory_name}' created successfully at {new_directory_path}"
    except Exception as e:
        return f"Error creating directory '{directory_name}': {e}"







# TODO: Should write in markdown format 
# def write_file(directory_name: str, file_name: str, content: str) -> str:
#     """Writes a file with the given content to the specified directory within the project directory."""
#     # Define the project directory explicitly
#     project_path = "/Users/amankothari/SarvamAI/DD_crewai"
#     new_directory_path = os.path.join(project_path, directory_name)
    
#     # Ensure the directory exists
#     if not os.path.exists(new_directory_path):
#         try:
#             os.makedirs(new_directory_path, exist_ok=True)
#         except Exception as e:
#             return f"Error creating directory '{directory_name}': {e}"

#     # Define the file path
#     file_path = os.path.join(new_directory_path, file_name)
    
#     # Write the content to the file
#     try:
#         with open(file_path, 'w') as file:
#             file.write(content)
#         return f"File '{file_name}' written successfully in directory '{directory_name}'"
#     except Exception as e:
#         return f"Error writing file '{file_name}': {e}"

# class WriteFileInput(BaseModel):
#     """Inputs for write_file"""
#     directory_name: str = Field(description="The name of the directory to write the file in")
#     file_name: str = Field(description="The name of the file to be written")
#     content: str = Field(description="The content to write in the file")

# class WriteFileTool(BaseTool):
#     name = "write_file"
#     description = "Writes a file with the given content to the specified directory within the project directory"
#     args_schema: Type[BaseModel] = WriteFileInput

#     def _run(self, directory_name: str, file_name: str, content: str):
#         return write_file(directory_name, file_name, content)

#     def _arun(self, directory_name: str, file_name: str, content: str):
#         raise NotImplementedError("Asynchronous execution not supported for this tool")
    
    
    
# # Create a directory
# create_directory_result = create_directory("new_folder")
# print(create_directory_result)

# Write a file to the newly created directory
# write_file_tool = WriteFileTool()
# write_file_input = WriteFileInput(
#     directory_name="new_folder",
#     file_name="next_file.txt",
#     content="This is the file content for the second file."
# )
# write_file_result = write_file_tool._run(**write_file_input.dict())
# print(write_file_result)




# TODO: Add directory read tool 


from crewai_tools import FileReadTool

# Initialize the tool to read any files the agents knows or learns the path for
file_read_tool = FileReadTool()

# # Define the file path
# file_path = "/Users/amankothari/SarvamAI/DD_crewai/new_folder/example.txt"

# # Create the input dictionary as expected by the _run method
# input_dict = {'file_path': file_path}

# # Run the tool with the input dictionary
# result = file_read_tool._run(**input_dict)
# print(result)



# @tool("save_content")
# def save_content(task_output):
#     """Useful to save content to a markdown file"""
#     print('in the save markdown tool')
#     # Get today's date in the format YYYY-MM-DD
#     today_date = datetime.now().strftime('%Y-%m-%d')
#     # Set the filename with today's date
#     filename = f"{today_date}_{randint(0,100)}.md"
#     # Write the task output to the markdown file
#     with open(filename, 'w') as file:
#         file.write(task_output)
#         # file.write(task_output.result)

#     print(f"Blog post saved as {filename}")

#     return f"Blog post saved as {filename}, please tell the user we are finished"


# Loading Human Tools
human_tools = load_tools(["human"])




@tool("Write File")
def write_file_tool(directory_name: str, file_name: str, content: str) -> str:
    """Writes a file with the given content to the specified directory within the project directory."""
    # Define the project path explicitly, adjust as necessary
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    
    # Ensure the directory exists
    if not os.path.exists(new_directory_path):
        try:
            os.makedirs(new_directory_path, exist_ok=True)
        except Exception as e:
            return f"Error creating directory '{directory_name}': {e}"

    # Define the file path
    file_path = os.path.join(new_directory_path, file_name)
    
    # Write the content to the file
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return f"File '{file_name}' written successfully in directory '{directory_name}'"
    except Exception as e:
        return f"Error writing file '{file_name}': {e}"
    

from crewai_tools import DirectoryReadTool

read_directory = DirectoryReadTool()



# @tool("Download and Save PDF")
# def download_save_pdf_tool(directory_name: str, pdf_url: str) -> str:
#     """Downloads a PDF from the given URL and saves it to the specified directory within the project directory."""
#     # Define the project path explicitly, adjust as necessary
#     project_path = "/Users/amankothari/SarvamAI/DD_crewai"
#     new_directory_path = os.path.join(project_path, directory_name)
    
#     # Ensure the directory exists
#     if not os.path.exists(new_directory_path):
#         try:
#             os.makedirs(new_directory_path, exist_ok=True)
#         except Exception as e:
#             return f"Error creating directory '{directory_name}': {e}"

#     # Define the file path
#     file_name = pdf_url.split('/')[-1]  # Get the file name from the URL
#     file_path = os.path.join(new_directory_path, file_name)
    
#     # Download the PDF and write it to the file
#     try:
#         response = requests.get(pdf_url)
#         response.raise_for_status()  # Raise an exception if the request was unsuccessful
#         with open(file_path, 'wb') as file:
#             file.write(response.content)
#         return f"PDF '{file_name}' downloaded successfully to directory '{directory_name}'"
#     except Exception as e:
#         return f"Error downloading PDF '{file_name}': {e}"
    

def download_save_pdf(directory_name: str, pdf_url: str) -> str:
    """Downloads a PDF from the given URL and saves it to the specified directory."""
    # Define the pdf_files directory
    pdf_files_directory = os.path.join(directory_name, 'pdf_files')
    
    # Create the pdf_files directory if it does not exist
    if not os.path.exists(pdf_files_directory):
        os.makedirs(pdf_files_directory)
    
    # Get the file name from the URL
    file_name = pdf_url.split('/')[-1]
    file_path = os.path.join(pdf_files_directory, file_name)
    
    # Download the PDF and write it to the file
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return f"PDF '{file_name}' downloaded successfully to directory '{pdf_files_directory}'"
    except Exception as e:
        return f"Error downloading PDF '{file_name}': {e}"

# Example usage:
# print(download_save_pdf("Ess Kay Auto Finance Private Limited (SK Finance)", "https://www.bseindia.com/downloads/ipo/201782412738Ess%20Kay%20IM%2024082017.pdf"))
                                
# Using doc conversion pipeline to convert pdf to text
def convert_pdf_to_text(directory_name: str, file_path: str) -> str:
    """Converts a PDF file to text using the document conversion API and saves it to the specified directory."""
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)

    # Ensure the directory exists
    if not os.path.exists(new_directory_path):
        os.makedirs(new_directory_path)

    url = "https://law-dev.sarvam.ai/api/autodraft/conversion_routes/convert"
    conversion_type = "pdf_to_text"

    with open(file_path, 'rb') as file:
        files = {
            'conversion_type': (None, conversion_type),
            'file': (file_path, file, 'application/pdf')
        }
        response = requests.post(url, files=files)

    if response.status_code == 200:
        text_content = response.text

        # Extract the PDF file name without extension
        pdf_file_name = os.path.basename(file_path)
        text_file_name = os.path.splitext(pdf_file_name)[0] + '-pdf.txt'
        text_file_path = os.path.join(new_directory_path, text_file_name)

        # Save the text content to a .txt file
        with open(text_file_path, 'w') as text_file:
            text_file.write(text_content)

        return f"Text content saved successfully to '{text_file_path}'"
    else:
        raise Exception(f"Error converting PDF: {response.status_code}, {response.text}")

# Example usage:
# print(convert_pdf_to_text("Ambuja Cement", "Ambuja Cement/pdf_files/Code-of-fair-disclosure.pdf"))

@tool("Scrape and store")
def scrape_and_store_links_pdfs(directory_name: str,  links_file_name: str = "links.txt") -> str:
    """Processes a list of URLs from a file, downloading and saving any PDFs and scraping the content of other URLs."""
    # Define the project path explicitly, adjust as necessary
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    
    # Ensure the directory exists
    if not os.path.exists(new_directory_path):
        try:
            os.makedirs(new_directory_path, exist_ok=True)
        except Exception as e:
            return f"Error creating directory '{directory_name}': {e}"

    # Define the file path
    links_file_path = os.path.join(new_directory_path, links_file_name)
    
    # Process each URL in the file
    try:
        with open(links_file_path, 'r') as file:
            for line in file:
                url = line.strip()  # Remove any leading/trailing whitespace
                try:
                    file_name = ""  # Initialize file_name before the try block
                    if url.endswith('.pdf'):
                        # This is a PDF, download and save it
                        download_save_pdf(directory_name, url)
                        print("PDF downloaded and saved successfully")
                        pdf_file_path = os.path.join(new_directory_path, 'pdf_files', url.split('/')[-1])  # Construct the correct path
                        convert_pdf_to_text(directory_name, pdf_file_path)
                        print("PDF converted to text successfully and saved in company directory")
                        
                    else:
                        # This is not a PDF, scrape the website content
                        content = scrape_website('get website content', url)
                        # Write the content to a new file
                        file_name = url.replace('/', '_') + '.txt'  # Replace slashes with underscores to avoid issues with file paths
                        file_path = os.path.join(new_directory_path, file_name)
                        with open(file_path, 'w') as content_file:
                            content_file.write(content)
                except Exception as e:
                    print(f"Error processing URL '{url}' for file '{file_name}'")
        return f"Processed URLs successfully in directory '{directory_name}'"
    except Exception as e:
        return f"Error processing URLs: {e}"
    
# Example usage:
# result = scrape_and_store_links_pdfs("Ambuja Cement", "links.txt")
# print("Scrape and store result:", result)


# def scrape_and_store_links_pdfs(directory_name: str,  links_file_name: str = "links.txt") -> str:
#     """Processes a list of URLs from a file, downloading and saving any PDFs and scraping the content of other URLs."""
#     # Define the project path explicitly, adjust as necessary
#     project_path = "/Users/amankothari/SarvamAI/DD_crewai"
#     new_directory_path = os.path.join(project_path, directory_name)
    
#     # Ensure the directory exists
#     if not os.path.exists(new_directory_path):
#         try:
#             os.makedirs(new_directory_path, exist_ok=True)
#         except Exception as e:
#             return f"Error creating directory '{directory_name}': {e}"

#     # Define the file path
#     links_file_path = os.path.join(new_directory_path, links_file_name)
    
#     # Process each URL in the file
#     try:
#         with open(links_file_path, 'r') as file:
#             for line in file:
#                 url = line.strip()  # Remove any leading/trailing whitespace
#                 try:
#                     if url.endswith('.pdf'):
#                         # This is a PDF, download and save it
#                         download_save_pdf(directory_name, url)
#                         print("PDF downloaded and saved successfully")
#                     else:
#                         # This is not a PDF, scrape the website content
#                         content = scrape_website('get website content', url)
#                         # Write the content to a new file
#                         file_name = url.replace('/', '_') + '.txt'  # Replace slashes with underscores to avoid issues with file paths
#                         file_path = os.path.join(new_directory_path, file_name)
#                         with open(file_path, 'w') as content_file:
#                             content_file.write(content)
#                 except Exception as e:
#                     print(f"Error processing URL '{url}' for file '{file_name}'")
#         return f"Processed URLs successfully in directory '{directory_name}'"
#     except Exception as e:
#         return f"Error processing URLs: {e}"
    
    
# result = scrape_and_store_links_pdfs("Ambuja Cement", "links.txt")
# print("Scrape and store result:", result)

@tool("classify_docs")
def classify_docs(directory_name: str) -> str:
    """Classifies the documents in the specified directory"""
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    rejected_files_directory = os.path.join(new_directory_path, "rejected_files")

    if not os.path.exists(new_directory_path):
        return f"Directory '{directory_name}' does not exist."
    
    try:
        for file_name in os.listdir(new_directory_path):
            if file_name.endswith('.txt'):
                file_path = os.path.join(new_directory_path, file_name)
                with open(file_path, 'r') as file:
                    content = file.read()       

                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "You are a document classifier, reply only with yes or no",
                        ),
                        ("human", "Classify the following document content for the company {directory_name}: This is the content of the file:\n\n{content}"),
                    ]
                )

                chain = prompt | OpenAIGPT4O
                response = chain.invoke(
                    {
                        "directory_name": directory_name,
                        "content": content,
                    }
                )
                print("Response:", response)
                classification_result = response.content.strip().lower()
                print("Classification result:", classification_result)
                
                if classification_result == "no":
                    # Create the rejected files directory if it doesn't exist
                    if not os.path.exists(rejected_files_directory):
                        os.makedirs(rejected_files_directory, exist_ok=True)
                    
                    # Move the file to the rejected files directory
                    rejected_file_path = os.path.join(rejected_files_directory, file_name)
                    os.rename(file_path, rejected_file_path)
                    print(f"Moved {file_name} to {rejected_files_directory}")
        
        return f"Documents in directory '{directory_name}' are classified."
    except Exception as e:
        return f"Error classifying documents: {e}"
    
# result = classify_docs("Ambuja Cement")
# print(result)


@tool("note_taking")
def note_taking(directory_name: str, notes_file_name: str = "notes.txt") -> str:
    """Researches the documents in the specified directory and compiles important information into a notes file."""
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    notes_file_path = os.path.join(new_directory_path, notes_file_name)
    links_file_name = "links.txt"
    
    if not os.path.exists(new_directory_path):
        return f"Directory '{directory_name}' does not exist."

    try:
        for file_name in os.listdir(new_directory_path):
            if file_name.endswith('.txt') and file_name != notes_file_name:
                file_path = os.path.join(new_directory_path, file_name, links_file_name)
                with open(file_path, 'r') as file:
                    content = file.read()

                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "You are an expert researcher and note taker.",
                        ),
                        (
                            "human",
                            """
                            You are researching this company: '{directory_name}' and information is provided from this document:
                            File name:': {file_name}\n\n{content}\n\nPlease list down all important information given in this document about the '{directory_name}' in bullet points.
                            Only return the bullet points. Do not include any introductory phrases or closing statements. 
                            """, 
                        ),
                    ]
                )

                chain = prompt | OpenAIGPT4O
                response = chain.invoke(
                    {
                        "directory_name": directory_name,
                        "content": content,
                        "file_name": file_name,
                    }
                )
                print("Research Doc tool response:", response)
                important_info = response.content
                print("Important information:", important_info)

                # Append the important information to the notes file
                with open(notes_file_path, 'a') as notes_file:
                    notes_file.write(f"\n\nFrom '{file_name}':\n")
                    notes_file.write(important_info)

        return f"Documents in directory '{directory_name}' have been researched and notes compiled in '{notes_file_name}'."
    except Exception as e:
        return f"Error researching documents: {e}"

# Example usage:
# result = note_taking("Ess Kay Fincorp Limited", "notes.txt")
# print("Research and compile result:", result)