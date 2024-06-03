
from langchain.tools import tool
import os

from langchain.agents import load_tools

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
    print("CONTENT:.....", text)

    if len(text) > 10000:
        output = summary(objective, text)
        return output
    else:
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

RESULTS_PER_QUESTION = 3

search = BingSearchAPIWrapper()

@tool("Web_Search")
def web_search(question: str) -> str:
    """Performs a web search and returns a list of links to the top results."""
    results = search.results(question, RESULTS_PER_QUESTION)
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
def write_file(directory_name: str, file_name: str, content: str) -> str:
    """Writes a file with the given content to the specified directory within the project directory."""
    # Define the project directory explicitly
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

class WriteFileInput(BaseModel):
    """Inputs for write_file"""
    directory_name: str = Field(description="The name of the directory to write the file in")
    file_name: str = Field(description="The name of the file to be written")
    content: str = Field(description="The content to write in the file")

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes a file with the given content to the specified directory within the project directory"
    args_schema: Type[BaseModel] = WriteFileInput

    def _run(self, directory_name: str, file_name: str, content: str):
        return write_file(directory_name, file_name, content)

    def _arun(self, directory_name: str, file_name: str, content: str):
        raise NotImplementedError("Asynchronous execution not supported for this tool")
    
    
    
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