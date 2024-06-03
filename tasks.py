from crewai import Task
from textwrap import dedent
from datetime import datetime   

class CustomTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def research_and_collect_docs(self, company, agent):
        return Task(
            description=dedent(f"""
                Research and collect comprehensive documents related to this company: '{company}'. 
                The current time is {datetime.now()}. Focus on gathering relevant information such as company website pages, 
                shareholding details, products and services, form fillings, public disclosures, and any other pertinent documents.
                
                Use advanced search techniques to find the required information, scrape the content from the identified websites, 
                and store the collected documents in a directory named after the company.

                Compile all the gathered documents in an organized manner within the specified directory.
            """),
            agent=agent,
			expected_output= """ 
            A complete collection of relevant documents related to the specified company, stored in an organized directory named after the company.
            """, 
			# callback = save_task_output, 
        )
        
    def analyze_and_take_notes(self, company_directory, agent):
        return Task(
            description=dedent(f"""
                Analyze and take detailed notes on the documents stored in the directory named '{company_directory}'. 
                The current time is {datetime.now()}. Focus on extracting key information from each document, such as financial figures, 
                legal stipulations, operational strategies, and other critical data.

                Read through each document carefully, and summarize the content into concise bullet-point notes. 
                Continuously update the 'notes.txt' file within the same directory with these notes, ensuring that all 
                points are clear, informative, and well-organized.

                Ensure that the notes provide a comprehensive and easy-to-understand overview of the essential aspects of each document.
            """),
            agent=agent,
            expected_output= """
            A detailed and organized 'notes.txt' file containing bullet-point notes from each analyzed document, 
            capturing key information and insights, stored in the directory named after the company.
            """,
            # callback = save_task_output, 
        )

    def find_and_record_regulations(self, notes_directory, agent):
        return Task(
            description=dedent(f"""
                Review and identify applicable Indian regulations based on the company information outlined in the 'notes.txt' file located in the '{notes_directory}' directory. The current time is {datetime.now()}. 

                Use the information from the notes to perform a detailed web search to find relevant regulations. Once appropriate regulations are identified on websites, use web scraping techniques to extract precise details about these regulations.

                Summarize the regulations and record them into a new file named 'applicable_regulations.txt' within the same directory. Ensure the regulations are correctly interpreted and applicable to the company's activities, maintaining legal accuracy and relevance.
            """),
            agent=agent,
            expected_output= """
            An 'applicable_regulations.txt' file containing all the regulations applicable to the company, derived from the information in the 'notes.txt' file and verified through web searches and scraping, stored in the specified directory.
            """,
            # callback = save_task_json, 
        )


    def generate_non_compliance_details(self, regulations_directory, agent):
        return Task(
            description=dedent(f"""
                Analyze the 'applicable_regulations.txt' file located in the '{regulations_directory}' directory. The current time is {datetime.now()}. Identify each regulation listed and conduct a detailed web search to determine the penalties for non-compliance associated with these regulations.

                Use web scraping techniques to extract specific information about penalties from relevant legal websites. Compile this data into concise descriptions of the consequences for each regulation.

                Record this information in a new file named 'non_compliance_penalties.txt' within the same directory. Ensure that each entry clearly indicates the regulation it pertains to and provides a detailed understanding of the penalties for non-compliance.
            """),
            agent=agent,
            expected_output= """
            A 'non_compliance_penalties.txt' file containing detailed descriptions of the penalties for non-compliance for each regulation listed in the 'applicable_regulations.txt' file, stored in the specified directory.
            """,
            # callback = save_task_json, 
        )

