from openai import OpenAI
from simple_salesforce import Salesforce
import os
from functools import lru_cache

class SalesforceAgent:
    def __init__(self, sf_username, sf_password, sf_token, limit=200):
        self.sf = Salesforce(username=sf_username, password=sf_password, security_token=sf_token)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message.content
        self._cache[str(lead_data)] = result
        return result
    
    def score_opportunity(self, opp_data):
        if str(opp_data) in self._cache:
            return self._cache[str(opp_data)]
        
        prompt = f"""Score this opportunity from 0-100 based on likelihood to close:
Opportunity: {opp_data}
Return only the numeric score and brief reason."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message.content
        self._cache[str(opp_data)] = result
        return result
    
    def generate_followup(self, record_data, record_type):
        prompt = f"""Generate 3 personalized follow-up actions for this {record_type}:
{record_data}
Be specific and actionable."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
