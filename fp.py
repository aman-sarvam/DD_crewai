import os
import json
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_community.utilities import BingSearchAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import tiktoken 


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

# RESULTS_PER_QUESTION = 3

load_dotenv()
serper_api_key = os.getenv("SERPER_API_KEY")

def search(query, num_results=5):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": query,
        "num" : num_results
        
    })

    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
        
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return []

    response_data = response.json()

    # Extracting the links from the response
    links = []
    for item in response_data.get('organic', []):
        if len(links) < num_results:
            links.append(item.get('link'))
        else:
            break

    return links

# Example usage:
# search_links = search("SK Finance", 24)
# print("Search links:", search_links)
# print("Length of search links: ", len(search_links))

def web_search(question: str, links_per_query: int) -> str:
    """Performs a web search and returns a list of links to the top results."""
    results = search.results(question, links_per_query)
    return [r["link"] for r in results]

def scrape_website_tool(objective: str, url: str) -> str:
    """Scrapes a website and optionally summarizes its content based on the given objective."""
    return scrape_website(objective, url)

def create_directory(directory_name: str) -> str:
    """Creates a directory with the given name in the project folder."""
    project_path = os.path.dirname(os.path.abspath(__file__))  # Assuming this script is in the project folder
    new_directory_path = os.path.join(project_path, directory_name)
    try:
        os.makedirs(new_directory_path, exist_ok=True)
        return f"Directory '{directory_name}' created successfully at {new_directory_path}"
    except Exception as e:
        return f"Error creating directory '{directory_name}': {e}"


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

# Fix the function to save the PDF file in the correct directory
# def download_save_pdf(directory_name: str, pdf_url: str) -> str:
#     """Downloads a PDF from the given URL and saves it to the specified directory."""
#     # Define the pdf_files directory
#     pdf_files_directory = os.path.join(directory_name, 'pdf_files')
    
#     # Create the pdf_files directory if it does not exist
#     if not os.path.exists(pdf_files_directory):
#         os.makedirs(pdf_files_directory)
    
#     # Get the file name from the URL
#     file_name = pdf_url.split('/')[-1]
    
#     # Ensure the PDF file is saved in the pdf_files directory
#     if file_name.startswith(directory_name):
#         file_name = file_name[len(directory_name):]

#     file_path = os.path.join(pdf_files_directory, file_name)
    
#     # Download the PDF and write it to the file
#     try:
#         response = requests.get(pdf_url)
#         response.raise_for_status()  # Raise an exception if the request was unsuccessful
#         with open(file_path, 'wb') as file:
#             file.write(response.content)
#         return f"PDF '{file_name}' downloaded successfully to directory '{pdf_files_directory}'"
#     except Exception as e:
#         return f"Error downloading PDF '{file_name}': {e}"


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

def compile_links_for_company(directory_name: str, num_results: int = 5) -> str:
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    links_file_path = os.path.join(new_directory_path, "links.txt")

    # Ensure the company directory exists
    if not os.path.exists(new_directory_path):
        os.makedirs(new_directory_path)

    queries = [
        "website pages pf ",
        "latest news on ",
        "annual report ",
        "management team of ",
        "investor relations for "
        "products and services of ",
        "public disclosures of ",
        "shareholding details of ",
        "form fillings of "
    ]
    
    all_links = []

    for query in queries:
        full_query = query + directory_name
        links = search(full_query, num_results=num_results)
        all_links.extend(links)

    # Write all links to links.txt file
    with open(links_file_path, 'w') as links_file:
        for link in all_links:
            links_file.write(link + "\n")

    return f"Links compiled and written to '{links_file_path}'"

# Example usage:
print(compile_links_for_company("SK Finance", 14))


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
                        print("Processing this pdf:", url)
                        download_save_pdf(directory_name, url)
                        
                        print("PDF downloaded and saved successfully")
                        pdf_file_path = os.path.join(new_directory_path, 'pdf_files', url.split('/')[-1])  # Construct the correct path
                        print("Converting PDF to text...")
                        convert_pdf_to_text(directory_name, pdf_file_path)
                        print("PDF converted to text successfully and saved in company directory")
                        
                    else:
                        # This is not a PDF, scrape the website content
                        content = scrape_website('get website content', url)
                        # Write the content to a new file
                        file_name = url.replace('/', '_') + '.txt'  
                        file_path = os.path.join(new_directory_path, file_name)
                        with open(file_path, 'w') as content_file:
                            content_file.write(content)
                except Exception as e:
                    print(f"Error processing URL '{url}' for file '{file_name}'")
        return f"Processed URLs successfully in directory '{directory_name}'"
    except Exception as e:
        return f"Error processing URLs: {e}"
    
# Example usage:
# result = scrape_and_store_links_pdfs("SK Finance Limited", "links.txt")
# print("Scrape and store result:", result)

# Truncate text content to the token limit
def truncate_text_to_token_limit(text_content, token_limit):
    tokenizer = tiktoken.encoding_for_model("gpt-4")
    tokens = tokenizer.encode(text_content)
    
    if len(tokens) > token_limit:
        truncated_tokens = tokens[:token_limit]
        truncated_text = tokenizer.decode(truncated_tokens)
        print("-------------Text Truncated-----------------")
        return truncated_text
    return text_content

def classify_docs(directory_name: str) -> str:
    """Classifies the documents in the specified directory"""
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    rejected_files_directory = os.path.join(new_directory_path, "rejected_files")
    links_file_name = "links.txt"

    pdf_directory_path = os.path.join(new_directory_path, "pdf_files")

    if not os.path.exists(new_directory_path):
        return f"Directory '{directory_name}' does not exist."
    
    token_limit = 40000

    try:
        for file_name in os.listdir(new_directory_path):
            if file_name.endswith('.txt') and file_name != links_file_name:
                file_path = os.path.join(new_directory_path, file_name)
                with open(file_path, 'r') as file:
                    content = file.read()

                # Truncate the content to the token limit
                truncated_content = truncate_text_to_token_limit(content, token_limit)
                
                escaped_content = truncated_content.replace("{", "{{").replace("}", "}}")


                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            """
                            # CONTEXT #
                            Document classification is a critical task in organizing and managing large volumes of documents. 
                            In the context of company-related information, it involves determining whether a given document contains relevant information about the company. 
                            This helps in filtering out irrelevant documents, ensuring that only pertinent information is retained for further analysis or reporting.

                            ###########
                            
                            
                            # OBJECTIVE #
                            
                            The current objective is to classify documents based on their relevance to the company. 
                            For each document provided, you need to decide if it contains any information related to the company. 
                            Your response should be limited to a simple "yes" or "no" based on your assessment.

                            You will be provided with the content of various documents. 
                            Your task is to read through each document and determine if it includes any information pertinent to the company. 
                            If the document contains relevant information, respond with "yes". If it does not, respond with "no". 

                            ############
                            
                            
                            # How to think #
                            1. Carefully review the content of each document provided to you.
                            2. Look for any references, data points, or sections that pertain to the company.
                            3. If you find information related to the company, respond with "yes".
                            4. If you do not find any information related to the company, respond with "no".
                            5. Your response should be clear and unambiguous, strictly limited to "yes" or "no".

                            NOTE: It is important to be accurate in your classification to ensure that all relevant documents are retained and irrelevant ones are discarded.

                            Now a human will give you the content of a document for you to classify based on the above criteria.
                            
                            ############                 
                            
                            """,
                        ),
                        ("human", f"Classify the following document content for the company {directory_name}: This is the content of the file:\n\n{escaped_content}"),
                    ]
                )

                chain = prompt | OpenAIGPT4O
                response = chain.invoke(
                    {
                        "directory_name": directory_name,
                        "content": truncated_content,
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
                    
                    # Delete the corresponding PDF file
                    
                    pdf_deleted_files_directory = os.path.join(new_directory_path, "pdf_deleted_files")
                    if not os.path.exists(pdf_deleted_files_directory):
                        os.makedirs(pdf_deleted_files_directory, exist_ok=True)
                    
    
                    pdf_file_name = file_name.replace('-pdf.txt', '.pdf')
                    pdf_file_path = os.path.join(pdf_directory_path, pdf_file_name)
                    pdf_deleted_file_path = os.path.join(pdf_deleted_files_directory, pdf_file_name)

                    if os.path.exists(pdf_file_path):
                        os.rename(pdf_file_path, pdf_deleted_file_path)
                        print(f"Moved corresponding PDF file to deleted files directory: {pdf_file_name}")
        
        return f"Documents in directory '{directory_name}' are classified."
    except Exception as e:
        return f"Error classifying documents: {e}"

# print(classify_docs("Ess Kay Auto Finance Private Limited (SK Finance)"))
# result = classify_docs("Ambuja Cement")
# print(result)

def split_text_into_chunks(text_content, chunk_size):
    tokenizer = tiktoken.encoding_for_model("gpt-4")
    tokens = tokenizer.encode(text_content)
    
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks

def get_important_info(directory_name, file_name, content):
    escaped_content = content.replace("{", "{{").replace("}", "}}")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                # CONTEXT #
                Extracting important company information is crucial for various business activities such as market research, competitor analysis, investment decision-making, and strategic planning. 
                The goal is to gather and summarize key information from company documents, reports, and other relevant files. 
                This process involves identifying and highlighting essential data points, metrics, and insights that can aid in decision-making and strategic planning.

                ###########
                
                
                # OBJECTIVE #
                
                The current objective is to extract important information from a provided company document and take bullet point notes. 
                The notes should be clear, concise, and well-organized, capturing all significant details from the document. 
                The information should be structured in a way that it can be easily referenced and utilized for further analysis or reporting.

                You will be provided with the content of a company document. You need to identify and extract key information, summarizing it into bullet points. 
                The notes should be comprehensive but succinct, ensuring that all critical points are covered without unnecessary verbosity.

                ############
                
                
                # How to think #
                1. Thoroughly review the provided company document to understand its content and context.
                2. Identify key information, including financial metrics, strategic initiatives, market position, competitive advantages, challenges, and other relevant data points.
                3. Summarize the identified information into bullet points.
                4. Organize the bullet points under appropriate headings for easy reference.
                5. Ensure that the notes are structured logically, with related information grouped together.

                NOTE: The notes should be factual and objective, avoiding any personal opinions or interpretations. The goal is to provide a clear and accurate summary of the company's information.

                Now a human will give you the content of the company document for you to extract important information and take bullet point notes.
                
                ############        
                """
                ,
            ),
            (
                "human",
                f"""
                You are researching this company: '{directory_name}' and information is provided from this document:
                File name: {file_name}\n\n{escaped_content}\n\nPlease list down all important information given in this document about the '{directory_name}' in bullet points.
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
    return response.content


def note_taking(directory_name: str, notes_file_name: str = "notes.txt") -> str:
    """Researches the documents in the specified directory and compiles important information into a notes file."""
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    notes_file_path = os.path.join(new_directory_path, notes_file_name)
    links_file_name = "links.txt"

    if not os.path.exists(new_directory_path):
        return f"Directory '{directory_name}' does not exist."

    # Ensure the notes file exists
    if not os.path.exists(notes_file_path):
        open(notes_file_path, 'w').close()

    try:
        for file_name in os.listdir(new_directory_path):
            if file_name.endswith('.txt') and file_name not in {notes_file_name, links_file_name}:
                file_path = os.path.join(new_directory_path, file_name)
                with open(file_path, 'r') as file:
                    content = file.read()
                
                tokenizer = tiktoken.encoding_for_model("gpt-4")
                tokens = tokenizer.encode(content)
                
                all_important_info = ""

                if len(tokens) > 100000:
                    chunk_size = 20000
                    chunks = split_text_into_chunks(content, chunk_size)
                    
                    for i, chunk in enumerate(chunks):
                        important_info = get_important_info(directory_name, f"{file_name} (Chunk {i+1})", chunk)
                        print("Important information:", important_info)
                        all_important_info += important_info + "\n"
                else:
                    all_important_info = get_important_info(directory_name, file_name, content)
                    print("Important information:", all_important_info)

                # Append the important information to the notes file
                with open(notes_file_path, 'a') as notes_file:
                    notes_file.write(f"\n\nFrom '{file_name}':\n")
                    notes_file.write(all_important_info)

        return f"Documents in directory '{directory_name}' have been researched and notes compiled in '{notes_file_name}'."
    except Exception as e:
        return f"Error researching documents: {e}"
    

# def create_segregated_notes(directory_name: str, notes_file_name: str = "notes.txt") -> str:
#     """Generates segregated notes with citations in a new text file based on the original notes file."""
#     project_path = "/Users/amankothari/SarvamAI/DD_crewai"
#     new_directory_path = os.path.join(project_path, directory_name)
#     notes_file_path = os.path.join(new_directory_path, notes_file_name)
    
#     if not os.path.exists(new_directory_path):
#         return f"Directory '{directory_name}' does not exist."
    
#     if not os.path.exists(notes_file_path):
#         return f"Notes file '{notes_file_name}' does not exist in directory '{directory_name}'."

#     try:
#         with open(notes_file_path, 'r') as file:
#             notes_content = file.read()

#         token_limit = 80000
#         truncated_content = truncate_text_to_token_limit(notes_content, token_limit)
#         escaped_content = truncated_content.replace("{", "{{").replace("}", "}}")

#         prompt = ChatPromptTemplate.from_messages(
#             [
#                 (
#                     "system",
#                     """
#                     # CONTEXT #
#                     Due Diligence is a common task conducted when a company is going to be acquired or merged with another company. The company needs to undergo due diligence
#                     to ensure that all the information about the company is accurate and up-to-date. This process involves reviewing all the documents, financial statements
#                     and other legal documents of the company. The due diligence report is a summary of all the information found during this process.
                    
#                     ###########
                    
                    
#                     # OBJECTIVE #
                    
#                     The current objective is to segregate the notes content provided, with citations indicating the source of each piece of information. 
#                     Each section of the notes should be clearly marked with its source file, and the information should be organized under relevant headings.
    
                    
#                     ############
                    
                    
#                     # How to think #
#                     1. Carefully read through the notes content provided.
#                     2. Identify the source file for each piece of information and make sure to include citations in the segregated notes.
#                     3. Organize the information under appropriate headings and sub-headings.
#                     4. Ensure that the notes are well-structured, and each piece of information is clearly cited with its source file.
#                     5. Do not modify any facts, as accuracy is crucial for due diligence.
#                     6. For sections where information is not available, leave them blank and state "Require more documents".

#                     Now a human will give you the notes content and the format for you to segregate and cite accordingly.
                    
#                     ############                 
                    
#                     """,
#                 ),
#                 (
#                     "human",
#                     f"""
#                     Hey, thanks for doing this. Please read below very carefully and ensure all points are followed before you create the segregated notes.

#                     The notes content provided below comes from various files. Your task is to segregate the information into relevant sections, and clearly cite each piece of information with the source file it came from.

#                     Possible format for sections in the company report are as follows:
#                     ```
#                     Due Diligence Report
#                     1. Overview and business of the company 
#                         1. Business of the company
#                         2. Key information: (from file: )
#                             1. Business segments 
#                             2. Branches
#                             3. Any other key details 
#                         3. Key findings (from file: )
#                             1. Financial performance
#                             2. Any other key finding 
#                     2. Corporate Details (from file: )
#                         1. Corporate Overview (Table format) (from file: )
#                             1. Name of the company
#                             2. Registered office
#                             3. Date of Incorporation 
#                             4. Place of Incorporation 
#                             5. Corporate Status
#                             6. Corporate Identification number (CIN)
#                             7. Authorized share capital 
#                             8. Paid up capital 
#                             9. Directors
#                                 1. Name, Nationality, Date of appointment, Type of director 
#                         2. Share Capital of the company 
#                             1. Details about paid up share capital and Equity shares 
#                             2. Dividend declaration 
#                                 1. Financial year, rate of dividend, amount of dividend, status of payment
#                         3. Investments by the company: 
#                             1. Any subsidiaries and associate companies 
#                             2. Other investment details 
#                         4. Constituent Document of the Company
#                             1. MOA summary 
#                                 1. Main objectives in the MOA
#                             2. AOA summary
#                         5. Board and Board Committees
#                             1. Board composition table 
#                             2. Board meetings:
#                                 1. Frequency 
#                                 2. Notice and agenda: do they comply with Companies Act 
#                                 3. Maintenance of Minutes: do they comply with Companies Act  
#                             3. Board committees:
#                                 1. Committee name, composition, designation, other observations 
#                         6. Share holder meetings: 
#                                 1. Frequency 
#                                 2. Notices for shareholder meeting: do they comply with Companies Act 
#                                 3. Minutes of the shareholder meeting : do they comply with Companies Act 
#                         7. Statutory Registers: 
#                                 1. Company has provided us with the copies of the following statutory registers: 
#                                         1. List of statutory registers 
#                         8. Corporate Social Responsibility
#                                 1. CSR Obligations 
#                                     1. Financial year, Expenditure in Rs. (Table format)
#                                 2. Did the company spend the required amount for CSR for each year
#                                 3. Review of CSR committee meeting minutes 
#                                 4. Any other information
#                         9. Ongoing Related party transactions: 
#                                 1. Table of related part transactions of specific year 
#                                     1. Details of the Contracting Party, name of interested director, name of relationship, nature of transaction, value of transaction as per last financial year 
#                         10. ROC Filings and Compliance Matters 
#                                 1. ROC Filings:
#                                     1. Review of ROC filings

#                     For sections where there is no information available, leave them blank and state "Require more documents".
#                     ```

#                     Notes Content:
#                     {escaped_content}
#                     """,
#                 ),
#             ]
#         )

#         chain = prompt | OpenAIGPT4O
#         response = chain.invoke(
#             {
#                 "directory_name": directory_name,
#                 "notes_content": escaped_content,
#             }
#         )
#         print("Create Segregated Notes tool response:", response)
#         segregated_notes = response.content
#         print("Generated Segregated Notes:", segregated_notes)

#         segregated_notes_file_path = os.path.join(new_directory_path, "segregated_notes.txt")
#         with open(segregated_notes_file_path, 'w') as segregated_notes_file:
#             segregated_notes_file.write(segregated_notes)

#         return f"Segregated notes with citations generated and saved to '{segregated_notes_file_path}'."
#     except Exception as e:
#         return f"Error generating segregated notes: {e}"
    
    
    
    
    
 

def create_report(directory_name: str, notes_file_name: str = "notes.txt") -> str:
    """Generates a due diligence report in HTML format based on the notes file."""
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)
    notes_file_path = os.path.join(new_directory_path, notes_file_name)
    
    if not os.path.exists(new_directory_path):
        return f"Directory '{directory_name}' does not exist."
    
    if not os.path.exists(notes_file_path):
        return f"Notes file '{notes_file_name}' does not exist in directory '{directory_name}'."

    try:
        with open(notes_file_path, 'r') as file:
            notes_content = file.read()

        token_limit = 80000
        truncated_content = truncate_text_to_token_limit(notes_content, token_limit)
        escaped_content = truncated_content.replace("{", "{{").replace("}", "}}")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    # CONTEXT #
                    Due Diligence is a common task conducted when a company is going to be acquired or merged with another company. The company needs to undergo due dilignce
                    to ensure that all the information about the company is accurate and up-to-date. This process involves reviewing all the documents, financial statements
                    and other legal documents of the company. The due diligence report is a summary of all the information found during this process.
                    
                    ###########
                    
                    
                    # OBJECTIVE #
                    
                    The current objective is to generate a due diligence report in HTML format based on the notes file provided. The report should include all the important information
                    and wherever the information is not available those sections of the report should be moved to the bottom of the report. It is important that Facts are not modified else 
                    there will be legal liability. There is no strict numbering required for the report but the report should be well-organized and structured. 
                    
                    You will be provided with the notes content from the notes file. You need to structure this information into a well-organized report which will eventually be converted 
                    into an HTML and Docx.
    
                    
                    ############
                    
                    
                    # How to think #
                    1. Look at the company report format
                    2. Compare the information and take a call on what should be the right heads under which we can put the information.
                    3. Wherever it is importnat for the information to be collated, it should be collated as a table or bullets. 
                    4. If there is a column within a table that is empty, that column should be deleted. We cannot have incomplete columns in the main report. 
                    5. The report should be crisp and concise. Even the layout has to be dense.
                    6. Begin the report with a section on key insights which should be synthesis of the notes content. You are not expected to state the facts here but make a synthesis of the facts.
                    NOTE: Synthesis is explaining the understanding of the facts in a concise manner with some extrapolation on things to look out for.
                    
                    Now a human will give you details on the sections that should be available in the company report and how to format the HTML.
                    
                    ############                 
                    
                    """,
                ),
                (
                    "human",
                    
                            f"""
                            Hey, thanks for doing this. Please read below very very carefully and ensure all points are followed before you create the report.
                            
                            Possible sections in the company report are as follows:
                            ```
                            Possilbe format for main report: 
                        
                            Due Dilligence Report
                            1. Overview and business of the company 
                                1. Business of the company
                                2. Key information: (from file: )
                                    1. Business segments 
                                    2. Branches
                                    3. Any other key details 
                                3. Key findings (from file: )
                                    1. Financial performance(preferably in table format) 
                                    2. Any other key finding 
                            2. Corporate Details (from file: )
                                1. Corporate Overview (Table format) (from file: )
                                    1. Name of the company
                                    2. Registered office
                                    3. Date of Incorporation 
                                    4. Place of Incorporation 
                                    5. Corporate Status
                                    6. Corporate Identification number (CIN)
                                    7. Authorized share capital 
                                    8. Paid up capital 
                                    9. Directors
                                        1. Name, Nationality, Date of appointment, Type of director (Separate table)
                                2. Share Capital of the company 
                                    1. Details about paid up share capital and Equity shares 
                                    2. Dividend declaration 
                                        1. Financial year, rate of dividend, amount of dividend, status of payment (Table format)
                                3. Investments by the company: 
                                    1. Any subsidiaries and associate companies 
                                    2. Other investment details 
                                4. Constituent Document of the Company
                                    1. MOA summary 
                                        1. Main objectives in the MOA
                                    2. AOA summary
                                5. Board and Board Committees
                                    1. Board composition table 
                                    2. Board meetings:
                                        1. Frequency 
                                        2. Notice and agenda: do they comply with Companies Act 
                                        3. Maintenance of Minutes: do they comply with Companies Act  
                                    3. Board committees:
                                        1. Committee name, composition, designation, other observations  (Table format)
                                6. Share holder meetings: 
                                        1. Frequency 
                                        2. Notices for shareholder meeting: do they comply with Companies Act 
                                        3. Minutes of the shareholder meeting : do they comply with Companies Act 
                                7. Statutory Registors: 
                                        1. Company has provided us with the copes of the following statutory registers: 
                                                1. List of statutory registers 
                                8. Corporate Social Responsibility
                                        1. CSR Obligations 
                                            1. Financial year, Expenditure in Rs. (Table format)
                                        2. Did the company spend the required amount for CSR for each year
                                        3. Review of CSR committee meeting minutes 
                                        4. Any other information
                                9. Ongoing Related party transactions: 
                                        1. Table of related part transactions of specific year 
                                            1. Details of the Contracting Party, name of interested director, name of relationship, nature of transaction, value of transaction as per last financial year 
                                10. ROC Fillings and Compliance Matters 
                                        1. ROC Fillings:
                                            1. Review of ROC fillings
                                    
                            ```
                            
                            DO NOT MAKE UP ANY INFORMATION. If for a section there is no information available, move that entire section at the end of the main report. This may require you to reformat the report and 
                            change the numbering.  If there is a column within a table that is empty, that column should be deleted. We cannot have incomplete columns in the main report. 
                            For someone reading this report we do not want missing information to be shown in various places. Hence, these sections needs to be placed at the end. 
                            just ADD "Require more documents for these sections:" as the title and add the sections below this heading.
                            
                            
                            For example: If you do not have enough information for the Share Capital of the company, Investments by the company, Board meetings, Corposate Social Responsibility section, add these
                            sections at the end of the report.  
                            
                            Formatting: 
                            - Use Times New Roman font, and single spacing, Text color should be black. This should apply to the tables in the html as well. Use internal CSS for this.  
                            - Ensure the HTML is clean, well-structured, and follows best practices for readability and accessibility.
                            
                            Things to note about HTML:
                            - When thinking about HTML formatting do think carefully and put points as bullets or sub-bullets. Whever bullets or sub-bullets
                            are required, they SHOULD BE INDENTED.
                            - Indentation is very IMPORTANT
                            - Avoid tables within tables. If needed seperate the tables.
                            - You are allowed to deviate from the provided format if you think it is necessary. But please do avoid tables within Table.
                            
                            Do not include any introductory or closing statements in the report. Do not start the reposse with "```html".
                            Start directly with <!DOCTYPE html>. 
                            
                            The notes also mentions while file the notes are from. Be sure to include the name of the file with the appropriate sections.

                            Notes:
                            {escaped_content}
                            """,
                    ),
            ]
        )

        chain = prompt | OpenAIGPT4O
        response = chain.invoke(
            {
                "directory_name": directory_name,
                "notes_content": escaped_content,
            }
        )
        print("Create Report tool response:", response)
        report_html = response.content
        print("Generated HTML Report:", report_html)

        report_file_path = os.path.join(new_directory_path, "due_diligence_report.html")
        with open(report_file_path, 'w') as report_file:
            report_file.write(report_html)

        return f"Due diligence report html generated and saved to '{report_file_path}'."
    except Exception as e:
        return f"Error generating report: {e}"
    

# Example usage:
# print(create_report("SK Finance Limited"))

 
 

 
 
 
 
 
 
 
def convert_html_to_docx(directory_name: str, file_path: str) -> str:
    """Converts an HTML file to a DOCX file using the document conversion API and saves it to the specified directory."""
    project_path = "/Users/amankothari/SarvamAI/DD_crewai"
    new_directory_path = os.path.join(project_path, directory_name)

    # Ensure the directory exists
    if not os.path.exists(new_directory_path):
        os.makedirs(new_directory_path)

    url = "https://law-dev.sarvam.ai/api/autodraft/conversion_routes/convert"
    conversion_type = "html_to_docx"

    with open(file_path, 'rb') as file:
        files = {
            'conversion_type': (None, conversion_type),
            'file': (file_path, file, 'text/html')
        }
        response = requests.post(url, files=files)

    if response.status_code == 200:
        docx_content = response.content

        # Extract the HTML file name without extension
        html_file_name = os.path.basename(file_path)
        docx_file_name = os.path.splitext(html_file_name)[0] + '-converted.docx'
        docx_file_path = os.path.join(new_directory_path, docx_file_name)

        # Save the DOCX content to a .docx file
        with open(docx_file_path, 'wb') as docx_file:
            docx_file.write(docx_content)

        return f"DOCX file saved successfully to '{docx_file_path}'"
    else:
        raise Exception(f"Error converting HTML: {response.status_code}, {response.text}")
    
# print(convert_html_to_docx("SK Finance Limited", "SK Finance Limited/due_diligence_report.html"))
 


# copmany_name = input("Enter company name: ")

# print("Creating directory....")
# print(create_directory(copmany_name))

# print("Creating links.txt file....")
# print(write_file_tool(copmany_name, "links.txt", ""))

# print(compile_links_for_company(copmany_name, 15))    
# print("Links added to links.txt file....")

# print("Scraping and storing links and PDFs....")
# print(scrape_and_store_links_pdfs("Sk Finance Limited", "links.txt"))

# print("Classifying documents....")
# print(classify_docs("Sk Finance Limited"))

# print("Taking notes....")
# print(note_taking("SK Finance Limited", "notes.txt"))

# print("Note taking completed....")

# print(create_report("SK Finance Limited", "notes.txt"))

# print(convert_html_to_docx("SK Finance Limited", "SK Finance Limited/due_diligence_report.html"))