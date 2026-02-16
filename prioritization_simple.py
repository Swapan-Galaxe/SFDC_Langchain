from openai import OpenAI
import json
import os

class LeadPrioritizer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def prioritize_leads(self, leads):
        scored_leads = []
        for lead in leads:
            score = self._calculate_score(lead)
            scored_leads.append({**lead, 'priority_score': score})
        return sorted(scored_leads, key=lambda x: x['priority_score'], reverse=True)
    
    def _calculate_score(self, lead):
        prompt = f"""Analyze this lead and return ONLY a number 0-100:
{json.dumps(lead)}
Consider: Rating, Status, LeadSource, Company size indicators.
Score only:"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        try:
            return int(''.join(filter(str.isdigit, response.choices[0].message.content[:3])))
        except:
            return 50

class OpportunityScorer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def score_opportunities(self, opportunities):
        scored_opps = []
        for opp in opportunities:
            score = self._calculate_score(opp)
            scored_opps.append({**opp, 'conversion_score': score})
        return sorted(scored_opps, key=lambda x: x['conversion_score'], reverse=True)
    
    def _calculate_score(self, opp):
        prompt = f"""Score this opportunity 0-100 for close likelihood:
{json.dumps(opp)}
Consider: Amount, StageName, Probability, CloseDate proximity.
Score only:"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        try:
            return int(''.join(filter(str.isdigit, response.choices[0].message.content[:3])))
        except:
            return 50

class FollowUpGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def generate_actions(self, record, record_type="lead"):
        prompt = f"""Generate 3 specific follow-up actions for this {record_type}:
{json.dumps(record)}

Format as numbered list with actionable steps."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
