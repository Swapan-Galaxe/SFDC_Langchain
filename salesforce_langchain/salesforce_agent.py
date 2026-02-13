from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from simple_salesforce import Salesforce
import os
from functools import lru_cache

class SalesforceAgent:
    def __init__(self, sf_username, sf_password, sf_token, limit=200):
        self.sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_token)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self._cache = {}
        self.limit = limit
        
    @lru_cache(maxsize=32)
    def get_leads(self, query=""):
        soql = f"SELECT Id, Name, Email, Company, Status, LeadSource, Rating FROM Lead WHERE IsConverted = false LIMIT {self.limit}"
        try:
            return self.sf.query(soql)['records']
        except Exception as e:
            return f"Error fetching leads: {str(e)}"
    
    @lru_cache(maxsize=32)
    def get_opportunities(self, query=""):
        soql = f"SELECT Id, Name, Amount, StageName, Probability, CloseDate, AccountId FROM Opportunity WHERE IsClosed = false LIMIT {self.limit}"
        try:
            return self.sf.query(soql)['records']
        except Exception as e:
            return f"Error fetching opportunities: {str(e)}"
    
    def score_lead(self, lead_data):
        if str(lead_data) in self._cache:
            return self._cache[str(lead_data)]
        prompt = f"""Score this lead from 0-100 based on conversion likelihood:
Lead: {lead_data}
Return only the numeric score and brief reason."""
        result = self.llm.invoke(prompt).content
        self._cache[str(lead_data)] = result
        return result
    
    def score_opportunity(self, opp_data):
        if str(opp_data) in self._cache:
            return self._cache[str(opp_data)]
        prompt = f"""Score this opportunity from 0-100 based on likelihood to close:
Opportunity: {opp_data}
Return only the numeric score and brief reason."""
        result = self.llm.invoke(prompt).content
        self._cache[str(opp_data)] = result
        return result
    
    def generate_followup(self, record_data, record_type):
        prompt = f"""Generate 3 personalized follow-up actions for this {record_type}:
{record_data}
Be specific and actionable."""
        return self.llm.invoke(prompt).content
    
    def create_agent(self):
        tools = [
            Tool(name="GetLeads", func=self.get_leads, description="Fetch active leads from Salesforce"),
            Tool(name="GetOpportunities", func=self.get_opportunities, description="Fetch open opportunities from Salesforce"),
            Tool(name="ScoreLead", func=self.score_lead, description="Score a lead's conversion likelihood"),
            Tool(name="ScoreOpportunity", func=self.score_opportunity, description="Score an opportunity's close likelihood"),
            Tool(name="GenerateFollowup", func=lambda x: self.generate_followup(x, "lead/opportunity"), description="Generate personalized follow-up actions")
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Salesforce AI assistant that prioritizes leads, scores opportunities, and suggests follow-ups."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True)

# Usage
if __name__ == "__main__":
    agent_system = SalesforceAgent(
        sf_username=os.getenv("SF_USERNAME"),
        sf_password=os.getenv("SF_PASSWORD"),
        sf_token=os.getenv("SF_TOKEN"),
        limit=500  # Process up to 500 records
    )
    
    executor = agent_system.create_agent()
    result = executor.invoke({"input": "Get top 5 leads, score them, and suggest follow-ups for the highest scored lead"})
    print(result)
