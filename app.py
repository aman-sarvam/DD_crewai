# -------------------------------------------------------------------- Required Imports 
from crewai import Crew, Process
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from agents import CustomAgents
from tasks import CustomTasks
from helper_functions import print_agent_output

# -------------------------------------------------------------------- Initializations and configurations
load_dotenv()
bing_subscription_key = os.getenv("BING_SUBSCRIPTION_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
os.environ["BING_SEARCH_URL"] = "https://api.bing.microsoft.com/v7.0/search"

OpenAIGPT4O = ChatOpenAI(
    model="gpt-4o"
)


class CustomCrew:
    def __init__(self, company):
        self.company = company

    def run(self):
        agents = CustomAgents()
        link_collector_agent = agents.collect_links()
        scrape_and_store_docs_agent = agents.scraoe_and_store_docs()
        review_docs_agent = agents.review_docs()
        note_taking_agent = agents.note_taker()
        # research_documents_collector_agent = agents.research_documents_collector()
        doc_review_note_taker_agent = agents.doc_review_note_taker()
        applicable_regulation_finder_agent = agents.applicable_regulation_finder() 
        # non_compliance_generator_agent = agents.non_compliance_generator()

        tasks = CustomTasks()
        collecting_links_task = tasks.collect_links(self.company, link_collector_agent)
        scrape_and_store_docs_task = tasks.scrape_and_store(scrape_and_store_docs_agent)
        review_docs_task = tasks.review_docs(review_docs_agent)
        note_taking_task = tasks.note_taking(note_taking_agent)
        # research_and_collect_docs_task = tasks.research_and_collect_docs(self.company, research_documents_collector_agent)
        analyze_and_take_notes_task = tasks.analyze_and_take_notes(self.company, doc_review_note_taker_agent)   
        find_and_record_regulations_task = tasks.find_and_record_regulations(self.company, applicable_regulation_finder_agent)
        # generate_non_compliance_details_task = tasks.generate_non_compliance_details(self.company, non_compliance_generator_agent)
        
        crew = Crew(
            agents=[link_collector_agent, scrape_and_store_docs_agent, review_docs_agent, note_taking_agent
                    # doc_review_note_taker_agent, applicable_regulation_finder_agent, 
                    ],
            tasks=[collecting_links_task,scrape_and_store_docs_task , review_docs_task, note_taking_task
                    #analyze_and_take_notes_task, find_and_record_regulations_task, 
                   ],
            verbose=2,
            process=Process.sequential,
            full_output=True,
            share_crew=False,
            step_callback=lambda x: print_agent_output(x,"MasterCrew Agent")
        )

        return crew.kickoff()

if __name__ == "__main__":
    print("## Welcome to the Custom Crew AI Project")
    print("-----------------------------------------")
    company = input("Enter company name: ")
    custom_crew = CustomCrew(company)
    result = custom_crew.run()
    print("\n\n########################")
    print("## Custom Crew Run Result:")
    print("########################\n")
    print(result)




