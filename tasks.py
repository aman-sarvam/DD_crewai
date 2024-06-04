from crewai import Task
from textwrap import dedent
from datetime import datetime   

class CustomTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"
    
    #Adding collect links task? 
    
    def collect_links(self, company, agent):
        return Task(
            description=dedent(f"""
            Create directory in the name of the company '{company}' and create a file named 'links.txt' within this directory. 
            Collect website links related to this company: '{company}'. 
            The current time is {datetime.now()}. The research will cover key aspects of the company: 
            website pages, shareholding details, products and services, form fillings, public disclosures. 

            Pick one aspect at a time and use the web search tool to find relevant links. Find 2 links for each aspect. Do this by giving 2 
            as the linkes_per_query parameter to the web search tool. Do not create sections in the 'links.txt' file. It should just contains the list of links.
            
            Once you have identified the links, store the links in the 'links.txt' file within the company directory. Each link should be on a new line.
            Aim to store at least 10 unique links.
        """),
        agent=agent,
        expected_output=""" 
        A complete collection of relevant documents related to the specified company, with contributions from around 90 different sources, stored in an organized directory named after the company.
        """, 
			# callback = save_task_output, 
        )
        
    
    def scrape_and_store(self, agent):
        return Task(
            description=dedent(f"""
            Using the read_directory tool read the name given to the links file. Pass the main directory name and the links file name 
            to the scrape_and_store_links_pdfs tool which will handles the scraping and storing completely. 
        """),
        agent=agent,
        expected_output=""" 
        A complete collection of relevant documents related to the specified company, with contributions from around 90 different sources, stored in an organized directory named after the company.
        """, 
        )   
        
    
    def review_docs(self, agent):
        return Task(
            description=dedent(f"""
            Uses the classify_docs tool to classify the documents in the directory. All process is handled by the tool.
            Just need to give it the company directory name.                  
            """),
            agent=agent,
            expected_output=""" 
            Documents in the company directory are correctly classified. 
            """, 
        )
    

    # def research_and_collect_docs(self, company, agent):
    #     return Task(
    #         description=dedent(f"""
    #         Research and collect comprehensive documents related to this company: '{company}'. 
    #         The current time is {datetime.now()}. The research will cover key aspects of the company: 
    #         website pages, shareholding details, products and services, form fillings, public disclosures. 

    #         Pick one aspect at a time and use the web search tool to find relevant links. Once you have identified the links, 
    #         use the scraping tool to get the text from each link and directly dump the text content returned by the scraping tool as it is into a file in the company directory 
    #         with the name of the file as the website name. 

    #         Do not analyze the text, just dump it into the file. 
    
    #     """),
    #     agent=agent,
    #     expected_output=""" 
    #     A complete collection of relevant documents related to the specified company, with contributions from around 90 different sources, stored in an organized directory named after the company.
    #     """, 
	# 		# callback = save_task_output, 
    #     )
        
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

